import os
import tempfile
import subprocess
import shutil

EXCEL_CONVERT_PS = """
param(
    [string]$xlsxPath,
    [string]$pdfPath,
    [string]$sheetName = ""
)

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$excel.ScreenUpdating = $false

try {
    # Open ReadOnly to prevent any prompts or file locks
    $wb = $excel.Workbooks.Open($xlsxPath, 0, $true)

    # Sanitize PO sheet if present to prevent COMException
    $poSheet = $null
    try { $poSheet = $wb.Sheets.Item('PO') } catch {}
    if ($poSheet -and ($poSheet.Range('F57').Text -like "*`t*")) {
        $poSheet.Range('F57').Value2 = ''
    }

    if ($sheetName -and $sheetName.Trim() -ne "") {
        $targetSheet = $wb.Sheets.Item($sheetName)
        # Export only the requested sheet
        $targetSheet.ExportAsFixedFormat(0, $pdfPath, 1) # 1 = xlQualityStandard
    } else {
        # Export all sheets
        $wb.ExportAsFixedFormat(0, $pdfPath, 1)
    }
} catch {
    Write-Error $_
    exit 1
} finally {
    if ($wb) { $wb.Close($false) }
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}
"""


def convert_with_libreoffice(xlsx_path, pdf_path, timeout_sec=40):
    """
    Headless conversion using LibreOffice (works on Linux/Docker production servers as well as Windows).
    """
    # Detect libreoffice / soffice command
    lo_cmd = shutil.which("libreoffice") or shutil.which("soffice")
    if not lo_cmd:
        # Check standard Windows paths if any
        for win_path in [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ]:
            if os.path.exists(win_path):
                lo_cmd = win_path
                break

    if not lo_cmd:
        return False

    out_dir = os.path.dirname(os.path.abspath(pdf_path))
    cmd = [
        lo_cmd,
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        out_dir,
        os.path.abspath(xlsx_path),
    ]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec)
        expected_pdf = os.path.join(out_dir, os.path.splitext(os.path.basename(xlsx_path))[0] + ".pdf")
        if os.path.exists(expected_pdf) and os.path.getsize(expected_pdf) > 0:
            if os.path.abspath(expected_pdf) != os.path.abspath(pdf_path):
                shutil.move(expected_pdf, pdf_path)
            return True
        elif os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            return True
    except Exception as e:
        print("LibreOffice conversion failed:", e)

    return False


def convert_workbook_to_pdf(workbook, sheet_name=None, timeout_sec=30):
    """
    Takes an openpyxl Workbook, exports it via native Microsoft Excel COM (Windows)
    or headless LibreOffice (Linux / Docker production servers).
    """
    temp_dir = tempfile.mkdtemp(prefix="pds_pdf_")
    xlsx_path = os.path.join(temp_dir, "temp.xlsx")
    pdf_path = os.path.join(temp_dir, "temp.pdf")
    ps_path = os.path.join(temp_dir, "convert.ps1")

    try:
        workbook.save(xlsx_path)

        # 1. On non-Windows platforms (e.g. Linux / Docker container), run LibreOffice
        if os.name != 'nt' or not shutil.which("powershell"):
            if convert_with_libreoffice(xlsx_path, pdf_path, timeout_sec=timeout_sec):
                with open(pdf_path, "rb") as f:
                    return f.read()
            return None

        # 2. On Windows, try native Excel COM via PowerShell
        with open(ps_path, "w", encoding="utf-8") as f:
            f.write(EXCEL_CONVERT_PS)

        cmd = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            ps_path,
            "-xlsxPath",
            os.path.abspath(xlsx_path),
            "-pdfPath",
            os.path.abspath(pdf_path),
            "-sheetName",
            sheet_name or "",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )

        if result.returncode == 0 and os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            with open(pdf_path, "rb") as f:
                return f.read()

        # 3. Fallback to LibreOffice if COM failed on Windows
        if convert_with_libreoffice(xlsx_path, pdf_path, timeout_sec=timeout_sec):
            with open(pdf_path, "rb") as f:
                return f.read()

        print("Excel COM PDF export error:", result.stderr)
        return None

    except Exception as e:
        print("Excel COM PDF conversion failed or timed out:", e)
        # Attempt fallback to LibreOffice
        try:
            if convert_with_libreoffice(xlsx_path, pdf_path, timeout_sec=timeout_sec):
                with open(pdf_path, "rb") as f:
                    return f.read()
        except Exception:
            pass
        return None
    finally:
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

POPULATE_AND_CONVERT_PS = """
param(
    [string]$templatePath,
    [string]$jsonCellsPath,
    [string]$pdfPath,
    [string]$sheetName = ""
)

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$excel.ScreenUpdating = $false

$tempXlsx = [System.IO.Path]::ChangeExtension($pdfPath, ".xlsx")

try {
    # 1. Copy template to a working copy so original is untouched
    Copy-Item $templatePath $tempXlsx -Force

    # 2. Open working copy in Excel
    $wb = $excel.Workbooks.Open($tempXlsx)

    # 3. Clean F57 in PO sheet to prevent COM exception
    try {
        $po = $wb.Sheets.Item('PO')
        if ($po) { $po.Range('F57').Value2 = '' }
    } catch {}

    # 4. Populate values from JSON cell map
    if (Test-Path $jsonCellsPath) {
        $jsonStr = [System.IO.File]::ReadAllText($jsonCellsPath, [System.Text.Encoding]::UTF8)
        $data = $jsonStr | ConvertFrom-Json
        
        foreach ($prop in $data.PSObject.Properties) {
            $wsName = $prop.Name
            try {
                $ws = $wb.Sheets.Item($wsName)
                if ($ws) {
                    $sheetCells = $prop.Value
                    foreach ($c in $sheetCells.PSObject.Properties) {
                        $cellAddr = $c.Name
                        $val = $c.Value
                        $ws.Range($cellAddr).Value2 = $val
                    }
                }
            } catch {}
        }
    }

    # 5. Export requested sheet or all sheets
    if ($sheetName -and $sheetName.Trim() -ne "") {
        $targetSheet = $wb.Sheets.Item($sheetName)
        $targetSheet.ExportAsFixedFormat(0, $pdfPath, 1)
    } else {
        $wb.ExportAsFixedFormat(0, $pdfPath, 1)
    }
} catch {
    Write-Error $_
    exit 1
} finally {
    if ($wb) { $wb.Close($false) }
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
    if (Test-Path $tempXlsx) { Remove-Item $tempXlsx -Force -ErrorAction SilentlyContinue }
}
"""


def convert_template_cells_to_pdf(template_path, cell_map, sheet_name=None, timeout_sec=30):
    """
    Directly copies the official Excel template, populates cell values natively via COM,
    and exports directly to PDF. Eliminates openpyxl corruption and reduces export time to <1.5s.
    """
    import json
    temp_dir = tempfile.mkdtemp(prefix="voucher_pdf_")
    json_path = os.path.join(temp_dir, "cells.json")
    pdf_path = os.path.join(temp_dir, "output.pdf")
    ps_path = os.path.join(temp_dir, "convert_direct.ps1")

    # On non-Windows / production Linux servers without PowerShell COM, skip to workbook conversion
    if os.name != 'nt' or not shutil.which("powershell"):
        return None

    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(cell_map, f, ensure_ascii=False)

        with open(ps_path, "w", encoding="utf-8") as f:
            f.write(POPULATE_AND_CONVERT_PS)

        cmd = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            ps_path,
            "-templatePath",
            os.path.abspath(template_path),
            "-jsonCellsPath",
            os.path.abspath(json_path),
            "-pdfPath",
            os.path.abspath(pdf_path),
            "-sheetName",
            sheet_name or "",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )

        if result.returncode == 0 and os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            with open(pdf_path, "rb") as f:
                return f.read()
        else:
            print("Direct COM PDF export error:", result.stderr)
            return None

    except Exception as e:
        print("Direct COM PDF conversion failed or timed out:", e)
        return None
    finally:
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

