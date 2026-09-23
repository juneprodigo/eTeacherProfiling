import os
import tempfile
import subprocess
import shutil

EXCEL_CONVERT_PS = """
param(
    [string]$xlsxPath,
    [string]$pdfPath
)

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$excel.ScreenUpdating = $false

try {
    # Open ReadOnly to prevent any prompts or file locks
    $wb = $excel.Workbooks.Open($xlsxPath, 0, $true)
    # 0 = xlTypePDF
    $wb.ExportAsFixedFormat(0, $pdfPath)
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


def convert_workbook_to_pdf(workbook, timeout_sec=25):
    """
    Takes an openpyxl Workbook, exports it via native Microsoft Excel COM
    using ExportAsFixedFormat(0), and returns the PDF bytes.
    Returns None if Microsoft Excel is not available or conversion fails.
    """
    temp_dir = tempfile.mkdtemp(prefix="pds_pdf_")
    xlsx_path = os.path.join(temp_dir, "pds_temp.xlsx")
    pdf_path = os.path.join(temp_dir, "pds_temp.pdf")
    ps_path = os.path.join(temp_dir, "convert.ps1")

    try:
        workbook.save(xlsx_path)

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
            print("Excel COM PDF export error:", result.stderr)
            return None

    except Exception as e:
        print("Excel COM PDF conversion failed or timed out:", e)
        return None
    finally:
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass
