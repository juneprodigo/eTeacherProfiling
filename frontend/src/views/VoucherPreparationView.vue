<template>
  <div class="voucher-management-container">
    <!-- Header Bar -->
    <div class="page-header">
      <div class="header-info">
        <h1 class="page-title">Voucher Preparation</h1>
        <p class="page-subtitle">
          Manage Transaction Flow, Requisition (RIS), Purchase Request (PR), Quotations (AOQ/Canvass), Purchase Order (PO), Inspection (IAR), and Disbursement Voucher (DV).
        </p>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary" @click="openCreateModal">
          <span class="icon">+</span> New Voucher Transaction
        </button>
      </div>
    </div>

    <!-- Flowchart Stage Navigation Pills / Summary -->
    <div class="flowchart-summary glass-card">
      <div class="flow-step" :class="{ active: filterType === 'ALL' }" @click="filterType = 'ALL'">
        <div class="flow-num">ALL</div>
        <div class="flow-label">All Transactions</div>
        <div class="flow-count">{{ store.transactions.length }}</div>
      </div>
      <div class="flow-step" :class="{ active: filterType === 'SUPPLIES' }" @click="filterType = 'SUPPLIES'">
        <div class="flow-num">1</div>
        <div class="flow-label">Purchase of Supplies</div>
        <div class="flow-count">{{ countByType('SUPPLIES') }}</div>
      </div>
      <div class="flow-step" :class="{ active: filterType === 'REPAIR' }" @click="filterType = 'REPAIR'">
        <div class="flow-num">2</div>
        <div class="flow-label">Repair & Maint.</div>
        <div class="flow-count">{{ countByType('REPAIR') }}</div>
      </div>
      <div class="flow-step" :class="{ active: filterType === 'CATERING' }" @click="filterType = 'CATERING'">
        <div class="flow-num">3</div>
        <div class="flow-label">Catering</div>
        <div class="flow-count">{{ countByType('CATERING') }}</div>
      </div>
      <div class="flow-step" :class="{ active: filterType === 'TRAVEL' }" @click="filterType = 'TRAVEL'">
        <div class="flow-num">4</div>
        <div class="flow-label">Travel</div>
        <div class="flow-count">{{ countByType('TRAVEL') }}</div>
      </div>
      <div class="flow-step" :class="{ active: filterType === 'TRAINING' }" @click="filterType = 'TRAINING'">
        <div class="flow-num">5</div>
        <div class="flow-label">Training</div>
        <div class="flow-count">{{ countByType('TRAINING') }}</div>
      </div>
      <div class="flow-step" :class="{ active: filterType === 'UTILITIES' }" @click="filterType = 'UTILITIES'">
        <div class="flow-num">6</div>
        <div class="flow-label">Electricity/Net</div>
        <div class="flow-count">{{ countByType('UTILITIES') }}</div>
      </div>
      <div class="flow-step" :class="{ active: filterType === 'LOAD' }" @click="filterType = 'LOAD'">
        <div class="flow-num">7</div>
        <div class="flow-label">Communication/Load</div>
        <div class="flow-count">{{ countByType('LOAD') }}</div>
      </div>
    </div>

    <!-- Search & Filter Controls -->
    <div class="filter-bar glass-card">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by Transaction Code, Payee, PR No., Cheque No., or Liquidation Code..."
        />
      </div>
      <div class="filter-group">
        <select v-model="filterStatus" class="form-select">
          <option value="ALL">All Statuses</option>
          <option value="DRAFT">Draft</option>
          <option value="PENDING_CANVASS">Pending Canvass</option>
          <option value="AWARDED">Canvass Awarded</option>
          <option value="PO_ISSUED">PO Issued</option>
          <option value="INSPECTED">Inspected & Accepted</option>
          <option value="VOUCHER_READY">DV Ready</option>
          <option value="COMPLETED">Completed</option>
        </select>
      </div>
    </div>

    <!-- Transaction Table List -->
    <div class="table-card glass-card">
      <div v-if="store.loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading Voucher Transactions...</p>
      </div>

      <div v-else-if="filteredTransactions.length === 0" class="empty-state">
        <div class="empty-icon">📂</div>
        <h3>No Voucher Transactions Found</h3>
        <p>Start by creating a new voucher transaction using the flowchart flow.</p>
        <button class="btn btn-primary" @click="openCreateModal">+ Create New Transaction</button>
      </div>

      <div v-else class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>
              <th>Trans Code</th>
              <th>Type</th>
              <th>Payee / Supplier</th>
              <th>Cheque / ADA</th>
              <th>Liquidation</th>
              <th>Gross Amount</th>
              <th>Net Due</th>
              <th>Items</th>
              <th>Status</th>
              <th class="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredTransactions" :key="item.id" class="table-row">
              <td class="code-cell font-mono">
                <strong>{{ item.transaction_code }}</strong>
              </td>
              <td>
                <span class="type-badge" :class="item.transaction_type.toLowerCase()">
                  {{ item.transaction_type_display }}
                </span>
              </td>
              <td>
                <div class="payee-title">{{ item.payee_supplier_name || '—' }}</div>
              </td>
              <td>
                <div v-if="item.cheque_number" class="sub-info">Chk: {{ item.cheque_number }}</div>
                <div v-else-if="item.ada_number" class="sub-info">ADA: {{ item.ada_number }}</div>
                <div v-else class="text-muted">—</div>
              </td>
              <td>
                <div class="sub-info">{{ item.liquidation_month || '—' }}</div>
                <small v-if="item.liquidation_code" class="text-muted">{{ item.liquidation_code }}</small>
              </td>
              <td class="amount-cell">₱{{ formatMoney(item.dv_gross_amount || item.total_amount) }}</td>
              <td class="amount-cell net font-bold">₱{{ formatMoney(item.dv_net_amount) }}</td>
              <td>
                <span class="badge-count">{{ item.items_count }} items</span>
              </td>
              <td>
                <span class="status-badge" :class="item.status.toLowerCase()">
                  {{ item.status_display }}
                </span>
              </td>
              <td class="text-right action-buttons">
                <button
                  class="btn-icon download-btn"
                  title="Download Appendix & Voucher Excel (.xlsx)"
                  @click="store.downloadExcel(item.id, item.transaction_code)"
                >
                  📥
                </button>
                <button
                  class="btn-icon edit-btn"
                  title="Edit & View All Forms"
                  @click="openEditModal(item.id)"
                >
                  ✏️
                </button>
                <button
                  class="btn-icon delete-btn"
                  title="Delete Voucher"
                  @click="confirmDelete(item)"
                >
                  🗑️
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Comprehensive Full-Screen / Modal Editor for Transaction & Appendices -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content glass-card modal-large">
        <div class="modal-header">
          <div class="header-left">
            <h2>{{ isEditing ? 'Edit Voucher Transaction: ' + form.transaction_code : 'Create Voucher Transaction' }}</h2>
            <div class="modal-subtitle">
              Follows DepEd & COA Voucher Preparation Flowchart (Appendix 60, 61, 62, 63, AOQ, and DV)
            </div>
          </div>
          <div class="header-right">
            <button v-if="isEditing" class="btn btn-secondary mr-2" @click="store.downloadExcel(form.id, form.transaction_code)">
              📥 Export Excel
            </button>
            <button class="btn-close" @click="closeModal">✕</button>
          </div>
        </div>

        <!-- Form Tabs -->
        <div class="modal-tabs">
          <button
            class="tab-btn"
            :class="{ active: currentTab === 'GENERAL' }"
            @click="currentTab = 'GENERAL'"
          >
            1. Trans & Liquidation
          </button>
          <button
            class="tab-btn"
            :class="{ active: currentTab === 'ITEMS' }"
            @click="currentTab = 'ITEMS'"
          >
            2. Items & Canvass (1, 2, 3)
          </button>
          <button
            class="tab-btn"
            :class="{ active: currentTab === 'RIS' }"
            @click="currentTab = 'RIS'"
          >
            3. RIS (Appendix 63)
          </button>
          <button
            class="tab-btn"
            :class="{ active: currentTab === 'PR' }"
            @click="currentTab = 'PR'"
          >
            4. PR (Appendix 60)
          </button>
          <button
            class="tab-btn"
            :class="{ active: currentTab === 'PO' }"
            @click="currentTab = 'PO'"
          >
            5. PO (Appendix 61)
          </button>
          <button
            class="tab-btn"
            :class="{ active: currentTab === 'IAR' }"
            @click="currentTab = 'IAR'"
          >
            6. IAR (Appendix 62)
          </button>
          <button
            class="tab-btn"
            :class="{ active: currentTab === 'DV' }"
            @click="currentTab = 'DV'"
          >
            7. Disbursement Voucher (DV)
          </button>
        </div>

        <div class="modal-body">
          <!-- TAB 1: General & Liquidation Info -->
          <div v-show="currentTab === 'GENERAL'" class="tab-pane">
            <div class="form-grid">
              <div class="form-group">
                <label>Transaction Code *</label>
                <input v-model="form.transaction_code" type="text" class="form-input" placeholder="e.g. TR-2026-001" required />
              </div>
              <div class="form-group">
                <label>Transaction Type *</label>
                <select v-model="form.transaction_type" class="form-select">
                  <option value="SUPPLIES">Purchase of Supplies</option>
                  <option value="REPAIR">Repair and Maintenance</option>
                  <option value="CATERING">Catering</option>
                  <option value="TRAVEL">Travel</option>
                  <option value="TRAINING">Training</option>
                  <option value="UTILITIES">Electricity / Internet</option>
                  <option value="LOAD">Load</option>
                </select>
              </div>
              <div class="form-group">
                <label>Workflow Status</label>
                <select v-model="form.status" class="form-select">
                  <option value="DRAFT">Draft</option>
                  <option value="PENDING_CANVASS">Pending Canvass</option>
                  <option value="AWARDED">Canvass Awarded</option>
                  <option value="PO_ISSUED">PO Issued</option>
                  <option value="INSPECTED">Inspected & Accepted</option>
                  <option value="VOUCHER_READY">Disbursement Voucher Ready</option>
                  <option value="COMPLETED">Completed</option>
                </select>
              </div>
              <div class="form-group">
                <label>Liquidation Month</label>
                <input v-model="form.liquidation_month" type="text" class="form-input" placeholder="e.g. October 2026" />
              </div>
              <div class="form-group">
                <label>Liquidation Code</label>
                <input v-model="form.liquidation_code" type="text" class="form-input" placeholder="e.g. LIQ-2026-10" />
              </div>
              <div class="form-group">
                <label>ORS / BURS Number</label>
                <input v-model="form.ors_number" type="text" class="form-input" placeholder="e.g. 2026-10-001" />
              </div>
              <div class="form-group">
                <label>ORS / BURS Date</label>
                <input v-model="form.ors_date" type="date" class="form-input" />
              </div>
              <div class="form-group">
                <label>ADA Number</label>
                <input v-model="form.ada_number" type="text" class="form-input" placeholder="e.g. ADA-2026-01" />
              </div>
              <div class="form-group">
                <label>ADA Date</label>
                <input v-model="form.ada_date" type="date" class="form-input" />
              </div>
            </div>

            <div class="section-title">Primary Payee / Supplier (Awardee)</div>
            <div class="form-grid">
              <div class="form-group">
                <label>Payee / Supplier Name *</label>
                <input v-model="form.payee_supplier_name" type="text" class="form-input" placeholder="e.g. Vicky's Hardware" />
              </div>
              <div class="form-group">
                <label>TIN / Employee No.</label>
                <input v-model="form.payee_tin" type="text" class="form-input" placeholder="e.g. 123-456-789-000" />
              </div>
              <div class="form-group span-2">
                <label>Address</label>
                <input v-model="form.payee_address" type="text" class="form-input" placeholder="Business address" />
              </div>
              <div class="form-group">
                <label>Cheque Number</label>
                <input v-model="form.cheque_number" type="text" class="form-input" placeholder="e.g. 0001234" />
              </div>
              <div class="form-group">
                <label>Cheque Date</label>
                <input v-model="form.cheque_date" type="date" class="form-input" />
              </div>
            </div>
          </div>

          <!-- TAB 2: Items & Canvass 1, 2, 3 (AOQ) -->
          <div v-show="currentTab === 'ITEMS'" class="tab-pane">
            <div class="tab-header-flex">
              <div>
                <h3 class="pane-title">Items Specifications & Canvass Bidders</h3>
                <p class="pane-desc">Enter item specs and compare unit prices for Canvass 1 (Winner/Awardee), Canvass 2, and Canvass 3.</p>
              </div>
              <button class="btn btn-secondary" @click="addItemRow">+ Add Item</button>
            </div>

            <!-- Canvass Suppliers Setup -->
            <div class="canvass-suppliers-box glass-card mb-4">
              <h4>Canvass Bidders (Abstract of Quotation)</h4>
              <div class="suppliers-grid">
                <div class="supplier-slot">
                  <div class="slot-badge slot-1">Supplier 1 (Awardee / Primary)</div>
                  <input v-model="form.payee_supplier_name" type="text" class="form-input" placeholder="Supplier 1 Name" />
                </div>
                <div class="supplier-slot">
                  <div class="slot-badge slot-2">Supplier 2</div>
                  <input v-model="supplier2.supplier_name" type="text" class="form-input" placeholder="Supplier 2 Name" />
                </div>
                <div class="supplier-slot">
                  <div class="slot-badge slot-3">Supplier 3</div>
                  <input v-model="supplier3.supplier_name" type="text" class="form-input" placeholder="Supplier 3 Name" />
                </div>
              </div>
            </div>

            <div class="table-responsive">
              <table class="data-table form-table">
                <thead>
                  <tr>
                    <th width="50">#</th>
                    <th width="120">Classification</th>
                    <th>Item Description</th>
                    <th width="80">Unit</th>
                    <th width="90">Qty</th>
                    <th width="130">Supplier 1 (₱)</th>
                    <th width="120">Total (₱)</th>
                    <th width="120">Supplier 2 (₱)</th>
                    <th width="120">Supplier 3 (₱)</th>
                    <th width="50"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in form.items" :key="index">
                    <td>{{ index + 1 }}</td>
                    <td>
                      <input v-model="item.classification" type="text" class="table-input" placeholder="Category" />
                    </td>
                    <td>
                      <input v-model="item.description" type="text" class="table-input" placeholder="Item description" required />
                    </td>
                    <td>
                      <input v-model="item.unit" type="text" class="table-input" placeholder="pcs" />
                    </td>
                    <td>
                      <input v-model.number="item.quantity" type="number" step="any" class="table-input" @input="recalcItemTotal(item)" />
                    </td>
                    <td>
                      <input v-model.number="item.unit_cost_1" type="number" step="0.01" class="table-input" @input="recalcItemTotal(item)" />
                    </td>
                    <td class="amount-cell">
                      ₱{{ formatMoney(item.quantity * item.unit_cost_1) }}
                    </td>
                    <td>
                      <input v-model.number="item.unit_cost_2" type="number" step="0.01" class="table-input" placeholder="0.00" />
                    </td>
                    <td>
                      <input v-model.number="item.unit_cost_3" type="number" step="0.01" class="table-input" placeholder="0.00" />
                    </td>
                    <td>
                      <button class="btn-icon delete-btn" title="Remove" @click="removeItemRow(index)">✕</button>
                    </td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td colspan="6" class="text-right font-bold">Grand Total (Canvass 1):</td>
                    <td class="amount-cell font-bold">₱{{ formatMoney(computedGrossAmount) }}</td>
                    <td colspan="3"></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          <!-- TAB 3: Requisition and Issue Slip (RIS - Appendix 63) -->
          <div v-show="currentTab === 'RIS'" class="tab-pane">
            <h3 class="pane-title">Appendix 63: Requisition and Issue Slip (RIS)</h3>
            <p class="pane-desc">Controls stock requisition and issue details.</p>
            <div class="form-grid">
              <div class="form-group">
                <label>RIS Number</label>
                <input v-model="form.ris_number" type="text" class="form-input" placeholder="e.g. RIS-2026-10" />
              </div>
              <div class="form-group">
                <label>Requisition Date</label>
                <input v-model="form.ris_date1" type="date" class="form-input" />
              </div>
              <div class="form-group">
                <label>Issue Date</label>
                <input v-model="form.ris_date2" type="date" class="form-input" />
              </div>
              <div class="form-group span-2">
                <label>Purpose</label>
                <textarea v-model="form.ris_purpose" class="form-textarea" rows="2" placeholder="State purpose of requisition..."></textarea>
              </div>
              <div class="form-group">
                <label>Requested By</label>
                <input v-model="form.ris_requested_by" type="text" class="form-input" />
              </div>
              <div class="form-group">
                <label>Approved By</label>
                <input v-model="form.ris_approved_by" type="text" class="form-input" />
              </div>
              <div class="form-group">
                <label>Issued By</label>
                <input v-model="form.ris_issued_by" type="text" class="form-input" />
              </div>
              <div class="form-group">
                <label>Received By</label>
                <input v-model="form.ris_received_by" type="text" class="form-input" />
              </div>
            </div>
          </div>

          <!-- TAB 4: Purchase Request (PR - Appendix 60) -->
          <div v-show="currentTab === 'PR'" class="tab-pane">
            <h3 class="pane-title">Appendix 60: Purchase Request (PR)</h3>
            <div class="form-grid">
              <div class="form-group">
                <label>PR Number</label>
                <input v-model="form.pr_number" type="text" class="form-input" placeholder="e.g. PR-2026-10" />
              </div>
              <div class="form-group">
                <label>PR Date</label>
                <input v-model="form.pr_date" type="date" class="form-input" />
              </div>
              <div class="form-group span-2">
                <label>PR Purpose</label>
                <textarea v-model="form.pr_purpose" class="form-textarea" rows="2" placeholder="Purchase request purpose..."></textarea>
              </div>
              <div class="form-group">
                <label>Requested By</label>
                <input v-model="form.pr_requested_by" type="text" class="form-input" />
              </div>
              <div class="form-group">
                <label>Approved By</label>
                <input v-model="form.pr_approved_by" type="text" class="form-input" />
              </div>
            </div>
          </div>

          <!-- TAB 5: Purchase Order (PO - Appendix 61) -->
          <div v-show="currentTab === 'PO'" class="tab-pane">
            <h3 class="pane-title">Appendix 61: Purchase Order (PO)</h3>
            <div class="form-grid">
              <div class="form-group">
                <label>PO Number</label>
                <input v-model="form.po_number" type="text" class="form-input" placeholder="e.g. 2026-04" />
              </div>
              <div class="form-group">
                <label>PO Date</label>
                <input v-model="form.po_date" type="date" class="form-input" />
              </div>
              <div class="form-group">
                <label>Mode of Procurement</label>
                <input v-model="form.po_mode_of_procurement" type="text" class="form-input" />
              </div>
              <div class="form-group">
                <label>Place of Delivery</label>
                <input v-model="form.po_place_of_delivery" type="text" class="form-input" />
              </div>
              <div class="form-group">
                <label>Delivery Term</label>
                <input v-model="form.po_delivery_term" type="text" class="form-input" />
              </div>
              <div class="form-group">
                <label>Payment Term</label>
                <input v-model="form.po_payment_term" type="text" class="form-input" />
              </div>
            </div>
          </div>

          <!-- TAB 6: Inspection & Acceptance Report (IAR - Appendix 62) -->
          <div v-show="currentTab === 'IAR'" class="tab-pane">
            <h3 class="pane-title">Appendix 62: Inspection & Acceptance Report (IAR)</h3>
            <div class="form-grid">
              <div class="form-group">
                <label>IAR Number</label>
                <input v-model="form.iar_number" type="text" class="form-input" placeholder="e.g. IAR-2026-10" />
              </div>
              <div class="form-group">
                <label>IAR Date</label>
                <input v-model="form.iar_date" type="date" class="form-input" />
              </div>
              <div class="form-group">
                <label>Invoice Number</label>
                <input v-model="form.iar_invoice_number" type="text" class="form-input" placeholder="Invoice / Sales Receipt No." />
              </div>
              <div class="form-group">
                <label>Invoice Date</label>
                <input v-model="form.iar_invoice_date" type="date" class="form-input" />
              </div>
              <div class="form-group">
                <label>Inspection Officer</label>
                <input v-model="form.iar_inspection_officer" type="text" class="form-input" />
              </div>
              <div class="form-group">
                <label>Property Custodian</label>
                <input v-model="form.iar_property_custodian" type="text" class="form-input" />
              </div>
            </div>
          </div>

          <!-- TAB 7: Disbursement Voucher (DV) & Tax Breakdown -->
          <div v-show="currentTab === 'DV'" class="tab-pane">
            <h3 class="pane-title">Disbursement Voucher (DV) & Tax Computations</h3>
            <p class="pane-desc">
              Computes Gross Amount, 5% and 1% Tax Withholding, and Net Amount Due as requested in flowchart.
            </p>
            <div class="form-grid">
              <div class="form-group">
                <label>DV Number</label>
                <input v-model="form.dv_number" type="text" class="form-input" placeholder="e.g. 2026-10-001" />
              </div>
              <div class="form-group">
                <label>DV Date</label>
                <input v-model="form.dv_date" type="date" class="form-input" />
              </div>
              <div class="form-group">
                <label>Mode of Payment</label>
                <select v-model="form.dv_mode_of_payment" class="form-select">
                  <option value="MDSCheck">MDSCheck</option>
                  <option value="Commercial Check">Commercial Check</option>
                  <option value="ADA">ADA</option>
                  <option value="Others">Others</option>
                </select>
              </div>
            </div>

            <!-- Tax Computation Cards -->
            <div class="dv-computation-card glass-card">
              <div class="dv-calc-row">
                <span class="calc-label">Gross Amount:</span>
                <span class="calc-val">₱{{ formatMoney(computedGrossAmount) }}</span>
              </div>
              <div class="dv-calc-row tax-row">
                <div class="tax-rate-input">
                  <span>Less: Percent 1</span>
                  <select v-model.number="form.dv_tax_rate1" class="mini-select">
                    <option :value="0.05">5% (VAT / Expanded)</option>
                    <option :value="0.03">3%</option>
                    <option :value="0.00">0%</option>
                  </select>
                </div>
                <span class="calc-val text-danger">- ₱{{ formatMoney(computedTax1) }}</span>
              </div>
              <div class="dv-calc-row tax-row">
                <div class="tax-rate-input">
                  <span>Less: Percent 2</span>
                  <select v-model.number="form.dv_tax_rate2" class="mini-select">
                    <option :value="0.01">1% (Withholding / Income)</option>
                    <option :value="0.02">2%</option>
                    <option :value="0.00">0%</option>
                  </select>
                </div>
                <span class="calc-val text-danger">- ₱{{ formatMoney(computedTax2) }}</span>
              </div>
              <div class="dv-calc-row total-tax-row">
                <span class="calc-label">Total Withholding Tax:</span>
                <span class="calc-val text-danger">- ₱{{ formatMoney(computedTax1 + computedTax2) }}</span>
              </div>
              <div class="dv-calc-row due-row">
                <span class="calc-label font-bold">NET AMOUNT DUE:</span>
                <span class="calc-val due-val">₱{{ formatMoney(computedNetAmount) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <div class="footer-left">
            <span class="auto-sum-hint">Total Gross: <strong>₱{{ formatMoney(computedGrossAmount) }}</strong> | Net Due: <strong>₱{{ formatMoney(computedNetAmount) }}</strong></span>
          </div>
          <div class="footer-right">
            <button class="btn btn-secondary" @click="closeModal">Cancel</button>
            <button class="btn btn-primary" :disabled="saving" @click="saveVoucher">
              {{ saving ? 'Saving...' : (isEditing ? 'Update Voucher' : 'Create Voucher') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useVoucherStore } from '@/stores/vouchers'

const store = useVoucherStore()

const searchQuery = ref('')
const filterType = ref('ALL')
const filterStatus = ref('ALL')
const showModal = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const currentTab = ref('GENERAL')

// Bidders for Canvass 2 & 3
const supplier2 = ref({ supplier_slot: 2, supplier_name: '', supplier_address: '', canvass_date: null })
const supplier3 = ref({ supplier_slot: 3, supplier_name: '', supplier_address: '', canvass_date: null })

const form = ref({
  id: null,
  transaction_code: '',
  transaction_type: 'SUPPLIES',
  status: 'DRAFT',
  liquidation_code: '',
  liquidation_month: '',
  ada_number: '',
  ada_date: null,
  ors_number: '',
  ors_date: null,

  payee_supplier_name: '',
  payee_address: '',
  payee_tin: '',
  cheque_number: '',
  cheque_date: null,
  total_amount: 0,

  ris_number: '',
  ris_date1: null,
  ris_date2: null,
  ris_purpose: '',
  ris_requested_by: 'AMALIA I. CONSIGNA',
  ris_approved_by: 'JUDY S. MOLINA',
  ris_issued_by: 'DIVINA D. NOBLEZA',
  ris_received_by: 'JENNY LYN A. TABUADA',

  pr_number: '',
  pr_date: null,
  pr_purpose: '',
  pr_requested_by: 'DIVINA D. NOBLEZA',
  pr_approved_by: 'JUDY S. MOLINA',

  po_number: '',
  po_date: null,
  po_mode_of_procurement: 'SMALL VALUE',
  po_place_of_delivery: 'NAGUILIAN ELEMENTARY SCHOOL',
  po_delivery_term: '1-2 DAY/S OF DELIVERY',
  po_payment_term: 'Check',

  iar_number: '',
  iar_date: null,
  iar_invoice_number: '',
  iar_invoice_date: null,
  iar_inspection_officer: 'JENNY LYN A. TABUADA',
  iar_property_custodian: 'DIVINA D. NOBLEZA',

  dv_number: '',
  dv_date: null,
  dv_mode_of_payment: 'MDSCheck',
  dv_tax_rate1: 0.05,
  dv_tax_rate2: 0.01,

  items: [],
  canvass_suppliers: []
})

onMounted(async () => {
  await store.fetchTransactions()
})

const countByType = (type) => {
  return store.transactions.filter(t => t.transaction_type === type).length
}

const filteredTransactions = computed(() => {
  return store.transactions.filter(item => {
    const matchesType = filterType.value === 'ALL' || item.transaction_type === filterType.value
    const matchesStatus = filterStatus.value === 'ALL' || item.status === filterStatus.value
    const query = searchQuery.value.toLowerCase().trim()
    const matchesSearch = !query ||
      (item.transaction_code && item.transaction_code.toLowerCase().includes(query)) ||
      (item.payee_supplier_name && item.payee_supplier_name.toLowerCase().includes(query)) ||
      (item.liquidation_code && item.liquidation_code.toLowerCase().includes(query)) ||
      (item.cheque_number && item.cheque_number.toLowerCase().includes(query)) ||
      (item.ors_number && item.ors_number.toLowerCase().includes(query))

    return matchesType && matchesStatus && matchesSearch
  })
})

const computedGrossAmount = computed(() => {
  return (form.value.items || []).reduce((acc, it) => {
    return acc + (Number(it.quantity || 0) * Number(it.unit_cost_1 || 0))
  }, 0)
})

const computedTax1 = computed(() => {
  return computedGrossAmount.value * (Number(form.value.dv_tax_rate1) || 0)
})

const computedTax2 = computed(() => {
  return computedGrossAmount.value * (Number(form.value.dv_tax_rate2) || 0)
})

const computedNetAmount = computed(() => {
  return computedGrossAmount.value - (computedTax1.value + computedTax2.value)
})

const formatMoney = (val) => {
  const num = Number(val || 0)
  return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const recalcItemTotal = (item) => {
  item.total_cost = (Number(item.quantity || 0) * Number(item.unit_cost_1 || 0))
}

const addItemRow = () => {
  form.value.items.push({
    item_number: form.value.items.length + 1,
    item_code: '',
    classification: 'Office Supplies',
    unit: 'pcs',
    description: '',
    quantity: 1,
    unit_cost_1: 0,
    total_cost: 0,
    unit_cost_2: 0,
    unit_cost_3: 0
  })
}

const removeItemRow = (index) => {
  form.value.items.splice(index, 1)
}

const openCreateModal = () => {
  isEditing.value = false
  currentTab.value = 'GENERAL'
  supplier2.value = { supplier_slot: 2, supplier_name: '', supplier_address: '', canvass_date: null }
  supplier3.value = { supplier_slot: 3, supplier_name: '', supplier_address: '', canvass_date: null }

  const autoCode = `TR-${new Date().getFullYear()}-${String(store.transactions.length + 1).padStart(3, '0')}`

  form.value = {
    id: null,
    transaction_code: autoCode,
    transaction_type: 'SUPPLIES',
    status: 'DRAFT',
    liquidation_code: '',
    liquidation_month: '',
    ada_number: '',
    ada_date: null,
    ors_number: '',
    ors_date: null,

    payee_supplier_name: '',
    payee_address: '',
    payee_tin: '',
    cheque_number: '',
    cheque_date: null,
    total_amount: 0,

    ris_number: '',
    ris_date1: null,
    ris_date2: null,
    ris_purpose: '',
    ris_requested_by: 'AMALIA I. CONSIGNA',
    ris_approved_by: 'JUDY S. MOLINA',
    ris_issued_by: 'DIVINA D. NOBLEZA',
    ris_received_by: 'JENNY LYN A. TABUADA',

    pr_number: '',
    pr_date: null,
    pr_purpose: '',
    pr_requested_by: 'DIVINA D. NOBLEZA',
    pr_approved_by: 'JUDY S. MOLINA',

    po_number: '',
    po_date: null,
    po_mode_of_procurement: 'SMALL VALUE',
    po_place_of_delivery: 'NAGUILIAN ELEMENTARY SCHOOL',
    po_delivery_term: '1-2 DAY/S OF DELIVERY',
    po_payment_term: 'Check',

    iar_number: '',
    iar_date: null,
    iar_invoice_number: '',
    iar_invoice_date: null,
    iar_inspection_officer: 'JENNY LYN A. TABUADA',
    iar_property_custodian: 'DIVINA D. NOBLEZA',

    dv_number: '',
    dv_date: null,
    dv_mode_of_payment: 'MDSCheck',
    dv_tax_rate1: 0.05,
    dv_tax_rate2: 0.01,

    items: [
      {
        item_number: 1,
        item_code: '',
        classification: 'Office Supplies',
        unit: 'pcs',
        description: 'Bond Paper A4',
        quantity: 10,
        unit_cost_1: 250,
        total_cost: 2500,
        unit_cost_2: 260,
        unit_cost_3: 255
      }
    ],
    canvass_suppliers: []
  }

  showModal.value = true
}

const openEditModal = async (id) => {
  try {
    const data = await store.fetchVoucher(id)
    isEditing.value = true
    currentTab.value = 'GENERAL'

    const sup2 = (data.canvass_suppliers || []).find(s => s.supplier_slot === 2)
    const sup3 = (data.canvass_suppliers || []).find(s => s.supplier_slot === 3)
    supplier2.value = sup2 ? { ...sup2 } : { supplier_slot: 2, supplier_name: '', supplier_address: '', canvass_date: null }
    supplier3.value = sup3 ? { ...sup3 } : { supplier_slot: 3, supplier_name: '', supplier_address: '', canvass_date: null }

    form.value = JSON.parse(JSON.stringify(data))
    showModal.value = true
  } catch (err) {
    alert('Failed to load voucher details.')
  }
}

const closeModal = () => {
  showModal.value = false
}

const saveVoucher = async () => {
  if (!form.value.transaction_code) {
    alert('Please enter a Transaction Code.')
    return
  }

  saving.value = true
  try {
    const canvass_suppliers = []
    if (form.value.payee_supplier_name) {
      canvass_suppliers.push({
        supplier_slot: 1,
        supplier_name: form.value.payee_supplier_name,
        supplier_address: form.value.payee_address || '',
        canvass_date: form.value.pr_date || null,
        is_awardee: true
      })
    }
    if (supplier2.value.supplier_name) {
      canvass_suppliers.push({
        supplier_slot: 2,
        supplier_name: supplier2.value.supplier_name,
        supplier_address: supplier2.value.supplier_address || '',
        canvass_date: supplier2.value.canvass_date || null,
        is_awardee: false
      })
    }
    if (supplier3.value.supplier_name) {
      canvass_suppliers.push({
        supplier_slot: 3,
        supplier_name: supplier3.value.supplier_name,
        supplier_address: supplier3.value.supplier_address || '',
        canvass_date: supplier3.value.canvass_date || null,
        is_awardee: false
      })
    }

    const payload = {
      ...form.value,
      canvass_suppliers
    }

    if (isEditing.value) {
      await store.updateVoucher(form.value.id, payload)
    } else {
      await store.createVoucher(payload)
    }
    showModal.value = false
  } catch (err) {
    alert('Error saving voucher transaction. Please check required fields.')
  } finally {
    saving.value = false
  }
}

const confirmDelete = async (item) => {
  if (confirm(`Are you sure you want to delete Voucher "${item.transaction_code}"?`)) {
    try {
      await store.deleteVoucher(item.id)
    } catch (err) {
      alert('Failed to delete voucher.')
    }
  }
}
</script>

<style scoped>
.voucher-management-container {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}
.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #fff;
  margin: 0;
}
.page-subtitle {
  color: #a0aec0;
  margin-top: 0.25rem;
  font-size: 0.95rem;
}

/* Flowchart Stage Summary Pills */
.flowchart-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(8px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.flow-step {
  padding: 0.75rem;
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}
.flow-step:hover {
  border-color: #6366f1;
  background: rgba(99, 102, 241, 0.15);
  transform: translateY(-2px);
}
.flow-step.active {
  border-color: #818cf8;
  background: rgba(99, 102, 241, 0.25);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}
.flow-num {
  font-size: 0.8rem;
  font-weight: bold;
  color: #818cf8;
}
.flow-label {
  font-size: 0.8rem;
  font-weight: 500;
  color: #e2e8f0;
  margin-top: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.flow-count {
  font-size: 1.1rem;
  font-weight: 700;
  color: #fff;
  margin-top: 0.25rem;
}

/* Filter Bar */
.filter-bar {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: rgba(30, 41, 59, 0.6);
  border-radius: 10px;
}
.search-box {
  flex: 1;
  display: flex;
  align-items: center;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 0 0.75rem;
}
.search-icon {
  margin-right: 0.5rem;
  opacity: 0.7;
}
.search-box input {
  width: 100%;
  background: transparent;
  border: none;
  padding: 0.6rem 0;
  color: #fff;
  outline: none;
}

/* Data Table */
.table-card {
  background: rgba(30, 41, 59, 0.6);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  overflow: hidden;
}
.table-responsive {
  overflow-x: auto;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}
.data-table th, .data-table td {
  padding: 0.9rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.data-table th {
  background: rgba(15, 23, 42, 0.8);
  color: #94a3b8;
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
}
.table-row:hover {
  background: rgba(255, 255, 255, 0.02);
}
.code-cell {
  color: #60a5fa;
}
.type-badge {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  background: rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
}
.status-badge {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  background: rgba(16, 185, 129, 0.2);
  color: #6ee7b7;
}
.status-badge.draft {
  background: rgba(148, 163, 184, 0.2);
  color: #cbd5e1;
}
.amount-cell {
  font-family: monospace;
  font-size: 0.95rem;
}
.amount-cell.net {
  color: #10b981;
}
.sub-info {
  font-size: 0.85rem;
  color: #cbd5e1;
}
.badge-count {
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

/* Actions */
.action-buttons {
  display: flex;
  gap: 0.4rem;
  justify-content: flex-end;
}
.btn-icon {
  background: rgba(255, 255, 255, 0.08);
  border: none;
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.95rem;
}
.btn-icon:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}
.download-btn:hover {
  background: rgba(16, 185, 129, 0.3);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1.5rem;
}
.modal-content.modal-large {
  width: 95%;
  max-width: 1200px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  background: #1e293b;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
  overflow: hidden;
}
.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-subtitle {
  font-size: 0.85rem;
  color: #94a3b8;
  margin-top: 0.2rem;
}
.btn-close {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 1.25rem;
  cursor: pointer;
}

/* Modal Tabs */
.modal-tabs {
  display: flex;
  gap: 0.4rem;
  padding: 0.5rem 1.5rem;
  background: rgba(15, 23, 42, 0.5);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  overflow-x: auto;
}
.tab-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  padding: 0.6rem 0.9rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  white-space: nowrap;
}
.tab-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
}
.tab-btn.active {
  color: #fff;
  background: #6366f1;
}

/* Modal Body */
.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}
.pane-title {
  font-size: 1.15rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
}
.pane-desc {
  font-size: 0.85rem;
  color: #94a3b8;
  margin: 0.25rem 0 1rem 0;
}
.tab-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

/* Form Styles */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.form-group.span-2 {
  grid-column: span 2;
}
.form-group label {
  font-size: 0.8rem;
  color: #94a3b8;
  font-weight: 500;
}
.form-input, .form-select, .form-textarea {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #fff;
  padding: 0.6rem 0.8rem;
  border-radius: 6px;
  font-size: 0.9rem;
  outline: none;
}
.form-input:focus, .form-select:focus, .form-textarea:focus {
  border-color: #6366f1;
}
.section-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #818cf8;
  margin: 1.25rem 0 0.75rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 0.4rem;
}

/* Canvass Suppliers Grid */
.canvass-suppliers-box {
  padding: 1rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 8px;
}
.canvass-suppliers-box h4 {
  margin: 0 0 0.75rem 0;
  font-size: 0.9rem;
  color: #cbd5e1;
}
.suppliers-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}
.slot-badge {
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 0.4rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
}
.slot-1 { background: rgba(16, 185, 129, 0.2); color: #6ee7b7; }
.slot-2 { background: rgba(59, 130, 246, 0.2); color: #93c5fd; }
.slot-3 { background: rgba(168, 85, 247, 0.2); color: #d8b4fe; }

/* Table Inputs */
.form-table .table-input {
  width: 100%;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #fff;
  padding: 0.4rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
}

/* DV Calculation Box */
.dv-computation-card {
  background: rgba(15, 23, 42, 0.8);
  border-radius: 10px;
  padding: 1.5rem;
  max-width: 600px;
  margin: 1.5rem auto 0 auto;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.dv-calc-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.dv-calc-row.due-row {
  border-top: 2px solid #6366f1;
  border-bottom: none;
  margin-top: 0.5rem;
  padding-top: 1rem;
}
.calc-label {
  color: #cbd5e1;
  font-size: 0.95rem;
}
.calc-val {
  font-family: monospace;
  font-size: 1.1rem;
}
.due-val {
  color: #10b981;
  font-size: 1.35rem;
  font-weight: 700;
}
.text-danger {
  color: #f87171;
}
.mini-select {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  margin-left: 0.5rem;
}

/* Modal Footer */
.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(15, 23, 42, 0.5);
}
.auto-sum-hint {
  font-size: 0.9rem;
  color: #94a3b8;
}
.auto-sum-hint strong {
  color: #fff;
}
.footer-right {
  display: flex;
  gap: 0.75rem;
}

/* Buttons */
.btn {
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.9rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-primary {
  background: #6366f1;
  color: #fff;
}
.btn-primary:hover {
  background: #4f46e5;
}
.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}
.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.18);
}
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Empty / Loading States */
.empty-state, .loading-state {
  text-align: center;
  padding: 3rem 1.5rem;
  color: #94a3b8;
}
.empty-icon {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem auto;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
