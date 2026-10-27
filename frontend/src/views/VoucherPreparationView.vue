<template>
  <div class="voucher-container">
    <!-- Header Bar -->
    <div class="view-header glass-panel">
      <div class="header-left">
        <h2>📑 Voucher Preparation</h2>
        <p class="subtitle">
          Comprehensive Procurement &amp; Liquidation Workflow (Appendix 60, 61, 62, 63, Abstract of Quotation, and Disbursement Voucher)
        </p>
      </div>
      <div class="header-right">
        <button
          class="btn-nav"
          :class="{ active: currentView === 'TRANSACTIONS' }"
          @click="currentView = 'TRANSACTIONS'"
        >
          <span>📋</span> Transactions Flow
        </button>
        <button
          class="btn-nav"
          :class="{ active: currentView === 'LIBRARIES' }"
          @click="currentView = 'LIBRARIES'"
        >
          <span>📚</span> Voucher Libraries
        </button>
        <button
          class="btn-nav report-btn"
          @click="openSummaryReportModal"
        >
          <span>📊</span> Summary Reports
        </button>
        <button v-if="currentView === 'TRANSACTIONS'" class="btn-primary" @click="openCreateModal">
          <span class="btn-icon">➕</span> New Voucher Transaction
        </button>
        <button v-else class="btn-primary" @click="openAddLibraryModal">
          <span class="btn-icon">➕</span> Add {{ currentLibCategoryLabel }}
        </button>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- VIEW 1: TRANSACTIONS FLOW & CRUD -->
    <!-- ========================================================================= -->
    <div v-if="currentView === 'TRANSACTIONS'" class="transactions-view-section">
      <!-- Flowchart Stage Navigation Pills / Summary -->
      <div class="flowchart-summary glass-panel">
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
          <div class="flow-label">Repair &amp; Maint.</div>
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
          <div class="flow-label">Electricity / Net</div>
          <div class="flow-count">{{ countByType('UTILITIES') }}</div>
        </div>
        <div class="flow-step" :class="{ active: filterType === 'LOAD' }" @click="filterType = 'LOAD'">
          <div class="flow-num">7</div>
          <div class="flow-label">Communication / Load</div>
          <div class="flow-count">{{ countByType('LOAD') }}</div>
        </div>
      </div>

      <!-- Search & Filter Controls -->
      <div class="filter-bar glass-panel">
        <div class="filter-top-row">
          <div class="search-box">
            <span class="search-icon">🔍</span>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search by Code, Payee, PR No., Cheque No., or Liquidation Code..."
              class="search-input"
            />
          </div>
          <div class="filter-actions">
            <select v-model="filterStatus" class="select-filter">
              <option value="ALL">All Workflow Statuses</option>
              <option value="DRAFT">Draft</option>
              <option value="PENDING_CANVASS">Pending Canvass</option>
              <option value="AWARDED">Canvass Awarded</option>
              <option value="PO_ISSUED">PO Issued</option>
              <option value="INSPECTED">Inspected &amp; Accepted</option>
              <option value="VOUCHER_READY">DV Ready</option>
              <option value="COMPLETED">Completed</option>
            </select>
            <div class="filter-info">
              Showing {{ filteredTransactions.length }} of {{ store.transactions.length }} transactions
            </div>
          </div>
        </div>

        <!-- Date Range Filter Row -->
        <div class="filter-date-row">
          <div class="date-filter-group">
            <span class="date-filter-label">📅 Filter by:</span>
            <select v-model="dateFilterField" class="select-filter-sm">
              <option value="created_at">Date Created</option>
              <option value="cheque_date">Cheque Date</option>
              <option value="ors_date">ORS Date</option>
              <option value="po_date">PO Date</option>
              <option value="pr_date">PR Date</option>
              <option value="dv_date">DV Date</option>
            </select>

            <div class="date-input-wrap">
              <label>From:</label>
              <input v-model="dateFrom" type="date" class="date-input-sm" />
            </div>

            <div class="date-input-wrap">
              <label>To:</label>
              <input v-model="dateTo" type="date" class="date-input-sm" />
            </div>

            <button
              v-if="dateFrom || dateTo"
              class="btn-clear-date"
              title="Clear date filter"
              @click="clearDateFilter"
            >
              ✕ Clear
            </button>
          </div>

          <!-- Quick Date Presets -->
          <div class="date-presets">
            <button
              class="preset-btn"
              :class="{ active: activeDatePreset === 'ALL' }"
              @click="applyDatePreset('ALL')"
            >
              All Time
            </button>
            <button
              class="preset-btn"
              :class="{ active: activeDatePreset === 'THIS_MONTH' }"
              @click="applyDatePreset('THIS_MONTH')"
            >
              This Month
            </button>
            <button
              class="preset-btn"
              :class="{ active: activeDatePreset === 'LAST_30' }"
              @click="applyDatePreset('LAST_30')"
            >
              Last 30 Days
            </button>
            <button
              class="preset-btn"
              :class="{ active: activeDatePreset === 'THIS_QUARTER' }"
              @click="applyDatePreset('THIS_QUARTER')"
            >
              This Qtr
            </button>
            <button
              class="preset-btn"
              :class="{ active: activeDatePreset === 'THIS_YEAR' }"
              @click="applyDatePreset('THIS_YEAR')"
            >
              This Year
            </button>
          </div>
        </div>
      </div>

      <!-- Transaction Table List -->
      <div class="content-table-wrapper glass-panel">
        <div v-if="store.loading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading Voucher Transactions...</p>
        </div>

        <div v-else-if="filteredTransactions.length === 0" class="empty-state">
          <div class="empty-icon">📂</div>
          <h3>No Voucher Transactions Found</h3>
          <p>Create a new voucher transaction using the official flowchart steps.</p>
          <button class="btn-primary mt-3" @click="openCreateModal">+ Create New Transaction</button>
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
                <td class="font-bold code-highlight">
                  {{ item.transaction_code }}
                </td>
                <td>
                  <span class="badge type-badge">{{ item.transaction_type_display }}</span>
                </td>
                <td>
                  <div class="payee-title font-semibold">{{ item.payee_supplier_name || '—' }}</div>
                </td>
                <td>
                  <div v-if="item.cheque_number" class="sub-info">Chk: {{ item.cheque_number }}</div>
                  <div v-else-if="item.ada_number" class="sub-info">ADA: {{ item.ada_number }}</div>
                  <div v-else class="text-muted">—</div>
                </td>
                <td>
                  <div class="sub-info font-medium">{{ item.liquidation_month || '—' }}</div>
                  <small v-if="item.liquidation_code" class="text-muted">{{ item.liquidation_code }}</small>
                </td>
                <td class="amount-cell">₱{{ formatMoney(item.dv_gross_amount || item.total_amount) }}</td>
                <td class="amount-cell net-due font-bold">₱{{ formatMoney(item.dv_net_amount) }}</td>
                <td>
                  <span class="badge-count">{{ item.items_count }} items</span>
                </td>
                <td>
                  <span class="badge status-badge" :class="item.status.toLowerCase()">
                    {{ item.status_display }}
                  </span>
                </td>
                <td class="text-right actions-cell">
                  <button
                    class="btn-action preview-pdf"
                    title="Preview Official PDF Forms"
                    @click="openPdfPreview(item.id, item.transaction_code)"
                  >
                    👁️ PDF
                  </button>
                  <button
                    class="btn-action export"
                    title="Export filled Appendix forms to Excel (.xlsx)"
                    @click="store.downloadExcel(item.id, item.transaction_code)"
                  >
                    📥 Excel
                  </button>
                  <button
                    class="btn-action sheet-shortcut po-btn"
                    title="PO Sheet (Appendix 61) CRUD & Review"
                    @click="openEditModal(item.id, 'PO')"
                  >
                    📦 PO
                  </button>
                  <button
                    class="btn-action sheet-shortcut ris-btn"
                    title="RIS Sheet (Appendix 63) CRUD & Review"
                    @click="openEditModal(item.id, 'RIS')"
                  >
                    📝 RIS
                  </button>
                  <button
                    class="btn-action sheet-shortcut pr-btn"
                    title="PR-A&m Sheet (Appendix 60) CRUD & Review"
                    @click="openEditModal(item.id, 'PR')"
                  >
                    📋 PR
                  </button>
                  <button
                    class="btn-action sheet-shortcut aoq-btn"
                    title="AOQ Sheet (Abstract of Quotation) CRUD & Review"
                    @click="openEditModal(item.id, 'ITEMS')"
                  >
                    ⚖️ AOQ
                  </button>
                  <button
                    class="btn-action sheet-shortcut iar-btn"
                    title="IAR Sheet (Appendix 62) CRUD & Review"
                    @click="openEditModal(item.id, 'IAR')"
                  >
                    🔍 IAR
                  </button>
                  <button
                    class="btn-action edit"
                    title="Edit and Review Full Transaction"
                    @click="openEditModal(item.id)"
                  >
                    ✏️
                  </button>
                  <button
                    class="btn-action delete"
                    title="Delete Transaction"
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
    </div>

    <!-- ========================================================================= -->
    <!-- VIEW 2: VOUCHER REFERENCE LIBRARIES MANAGEMENT -->
    <!-- ========================================================================= -->
    <div v-else class="libraries-view-section">
      <!-- Tabs for Library Categories -->
      <div class="tabs-container glass-panel">
        <button
          v-for="cat in libraryCategories"
          :key="cat.key"
          class="tab-btn"
          :class="{ active: selectedLibCategory === cat.key }"
          @click="selectedLibCategory = cat.key"
        >
          <span class="tab-icon">{{ cat.icon }}</span>
          <span>{{ cat.label }}</span>
          <span class="tab-badge">{{ getLibraryCount(cat.key) }}</span>
        </button>
      </div>

      <!-- Library Search & Actions -->
      <div class="filter-bar glass-panel">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input
            v-model="libSearchQuery"
            type="text"
            :placeholder="`Search ${currentLibCategoryLabel}...`"
            class="search-input"
          />
        </div>
        <div class="filter-actions">
          <div class="filter-info">
            Showing {{ filteredLibraries.length }} of {{ getLibraryCount(selectedLibCategory) }} items
          </div>
          <button class="btn-primary" @click="openAddLibraryModal">
            <span class="btn-icon">➕</span> Add New {{ currentLibCategoryLabel }}
          </button>
        </div>
      </div>

      <!-- Library Table -->
      <div class="content-table-wrapper glass-panel">
        <table class="data-table">
          <thead>
            <tr>
              <th width="80">Order</th>
              <th>Name / Label</th>
              <th v-if="selectedLibCategory === 'TRANSACTION_TYPE'">Code</th>
              <th v-if="selectedLibCategory === 'SUPPLIER'">Address</th>
              <th v-if="selectedLibCategory === 'SUPPLIER'">TIN</th>
              <th v-if="['REQUESTED_BY', 'APPROVED_BY', 'ISSUED_BY', 'RECEIVED_BY'].includes(selectedLibCategory)">Designation / Office</th>
              <th width="100">Status</th>
              <th class="text-right" width="120">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredLibraries" :key="item.id">
              <td>{{ item.sort_order }}</td>
              <td class="font-bold">{{ item.name }}</td>
              <td v-if="selectedLibCategory === 'TRANSACTION_TYPE'">
                <span class="code-badge font-mono">{{ item.code || '—' }}</span>
              </td>
              <td v-if="selectedLibCategory === 'SUPPLIER'">{{ item.address || '—' }}</td>
              <td v-if="selectedLibCategory === 'SUPPLIER'">{{ item.tin || '—' }}</td>
              <td v-if="['REQUESTED_BY', 'APPROVED_BY', 'ISSUED_BY', 'RECEIVED_BY'].includes(selectedLibCategory)">
                {{ item.designation || '—' }}
              </td>
              <td>
                <span class="badge" :class="item.is_active ? 'active-badge' : 'inactive-badge'">
                  {{ item.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="text-right actions-cell">
                <button class="btn-action edit" title="Edit" @click="openEditLibraryModal(item)">✏️</button>
                <button class="btn-action delete" title="Delete" @click="deleteLibraryItem(item)">🗑️</button>
              </td>
            </tr>
            <tr v-if="filteredLibraries.length === 0">
              <td colspan="7" class="no-records">No reference library records found for this category.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- FULL-SCREEN MODAL: VOUCHER TRANSACTION & FORMS EDITOR -->
    <!-- ========================================================================= -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content glass-panel modal-fullscreen">
        <!-- Modal Top Bar -->
        <div class="modal-header">
          <div class="header-left">
            <h2>{{ isEditing ? 'Edit Voucher Transaction: ' + form.transaction_code : 'Create Voucher Transaction' }}</h2>
            <div class="modal-subtitle">
              Interactive Form Generation for DepEd &amp; Naguilian Elementary School (Appendix 60, 61, 62, 63, AOQ, and DV)
            </div>
          </div>
          <div class="header-right">
            <button v-if="isEditing" class="btn-action preview-pdf mr-2" @click="openPdfPreview(form.id, form.transaction_code)">
              👁️ Preview PDF
            </button>
            <button v-if="isEditing" class="btn-secondary mr-2" @click="store.downloadExcel(form.id, form.transaction_code)">
              📥 Export Excel (.xlsx)
            </button>
            <button class="btn-close" @click="closeModal">✕</button>
          </div>
        </div>

        <!-- Validation Error Alert Banner -->
        <div v-if="validationErrors.length > 0" class="validation-banner">
          <div class="banner-icon">⚠️</div>
          <div class="banner-content">
            <strong>Incomplete or Invalid Data Entry ({{ validationErrors.length }} {{ validationErrors.length === 1 ? 'field' : 'fields' }} require attention):</strong>
            <ul>
              <li v-for="(err, idx) in validationErrors" :key="idx" @click="currentTab = err.tab" class="error-link">
                {{ err.message }} <span class="tab-jump-hint">(Go to Tab {{ err.tabName }})</span>
              </li>
            </ul>
          </div>
          <button class="btn-clear-errors" @click="validationErrors = []" title="Dismiss error banner">✕</button>
        </div>

        <!-- Wizard / Form Tabs (Styled after PDS section wizard tabs) -->
        <div class="wizard-nav glass-panel">
          <button
            class="nav-tab"
            :class="{ active: currentTab === 'GENERAL', 'has-tab-error': hasTabErrors('GENERAL') }"
            @click="currentTab = 'GENERAL'"
          >
            <span class="tab-index">1</span>
            <span>Transaction &amp; Liquidation</span>
            <span v-if="hasTabErrors('GENERAL')" class="tab-error-dot" title="Missing required fields">!</span>
          </button>
          <button
            class="nav-tab"
            :class="{ active: currentTab === 'ITEMS', 'has-tab-error': hasTabErrors('ITEMS') }"
            @click="currentTab = 'ITEMS'"
          >
            <span class="tab-index">2</span>
            <span>Items &amp; AOQ (Abstract of Quotation)</span>
            <span v-if="hasTabErrors('ITEMS')" class="tab-error-dot" title="Missing required fields">!</span>
          </button>
          <button
            class="nav-tab"
            :class="{ active: currentTab === 'RIS', 'has-tab-error': hasTabErrors('RIS') }"
            @click="currentTab = 'RIS'"
          >
            <span class="tab-index">3</span>
            <span>RIS (Sheet 'RIS' / App. 63)</span>
            <span v-if="hasTabErrors('RIS')" class="tab-error-dot" title="Missing required fields">!</span>
          </button>
          <button
            class="nav-tab"
            :class="{ active: currentTab === 'PR', 'has-tab-error': hasTabErrors('PR') }"
            @click="currentTab = 'PR'"
          >
            <span class="tab-index">4</span>
            <span>PR (Sheet 'PR-A&m' / App. 60)</span>
            <span v-if="hasTabErrors('PR')" class="tab-error-dot" title="Missing required fields">!</span>
          </button>
          <button
            class="nav-tab"
            :class="{ active: currentTab === 'PO', 'has-tab-error': hasTabErrors('PO') }"
            @click="currentTab = 'PO'"
          >
            <span class="tab-index">5</span>
            <span>PO (Sheet 'PO' / App. 61)</span>
            <span v-if="hasTabErrors('PO')" class="tab-error-dot" title="Missing required fields">!</span>
          </button>
          <button
            class="nav-tab"
            :class="{ active: currentTab === 'IAR', 'has-tab-error': hasTabErrors('IAR') }"
            @click="currentTab = 'IAR'"
          >
            <span class="tab-index">6</span>
            <span>IAR (Sheet 'IAR' / App. 62)</span>
            <span v-if="hasTabErrors('IAR')" class="tab-error-dot" title="Missing required fields">!</span>
          </button>
          <button
            class="nav-tab"
            :class="{ active: currentTab === 'DV', 'has-tab-error': hasTabErrors('DV') }"
            @click="currentTab = 'DV'"
          >
            <span class="tab-index">7</span>
            <span>DV (Sheet 'DV')</span>
            <span v-if="hasTabErrors('DV')" class="tab-error-dot" title="Missing required fields">!</span>
          </button>
        </div>

        <!-- Modal Body Content -->
        <div class="modal-body">
          <!-- TAB 1: General & Liquidation Info -->
          <div v-show="currentTab === 'GENERAL'" class="form-section">
            <div class="section-title-row">
              <div>
                <h3>Transaction Code &amp; Liquidation Details</h3>
                <p class="section-sub">Initial flowchart stage: code, type, ORS/BURS, ADA, and Payee</p>
              </div>
              <span class="sheet-indicator">Header &amp; Accounting</span>
            </div>

            <h4 class="sub-heading">Transaction Classification</h4>
            <div class="form-grid-4">
              <div class="field" :class="{ 'field-has-error': isFieldInvalid('transaction_code') }">
                <label>1. Transaction Code * <span v-if="isFieldInvalid('transaction_code')" class="req-star font-bold text-danger">(Required)</span></label>
                <input
                  v-model="form.transaction_code"
                  type="text"
                  placeholder="e.g. TR-2026-001"
                  :class="{ 'input-invalid': isFieldInvalid('transaction_code') }"
                  @input="clearFieldError('transaction_code')"
                  required
                />
                <span v-if="isFieldInvalid('transaction_code')" class="error-inline-msg">Transaction code is required.</span>
              </div>
              <div class="field" :class="{ 'field-has-error': isFieldInvalid('transaction_type') }">
                <label>2. Transaction Type * (From Library) <span v-if="isFieldInvalid('transaction_type')" class="req-star font-bold text-danger">(Required)</span></label>
                <select
                  v-model="form.transaction_type"
                  :class="{ 'input-invalid': isFieldInvalid('transaction_type') }"
                  @change="clearFieldError('transaction_type')"
                >
                  <option
                    v-for="opt in getLibraryOptions('TRANSACTION_TYPE')"
                    :key="opt.code || opt.name"
                    :value="opt.code || opt.name"
                  >
                    {{ opt.name }}
                  </option>
                  <!-- Fallback options if library not seeded -->
                  <option v-if="!getLibraryOptions('TRANSACTION_TYPE').length" value="SUPPLIES">Purchase of Supplies</option>
                  <option v-if="!getLibraryOptions('TRANSACTION_TYPE').length" value="REPAIR">Repair and Maintenance</option>
                  <option v-if="!getLibraryOptions('TRANSACTION_TYPE').length" value="CATERING">Catering</option>
                  <option v-if="!getLibraryOptions('TRANSACTION_TYPE').length" value="TRAVEL">Travel</option>
                  <option v-if="!getLibraryOptions('TRANSACTION_TYPE').length" value="TRAINING">Training</option>
                  <option v-if="!getLibraryOptions('TRANSACTION_TYPE').length" value="UTILITIES">Electricity / Internet</option>
                  <option v-if="!getLibraryOptions('TRANSACTION_TYPE').length" value="LOAD">Load</option>
                </select>
                <span v-if="isFieldInvalid('transaction_type')" class="error-inline-msg">Please select transaction type.</span>
              </div>
              <div class="field">
                <label>3. Workflow Status</label>
                <select v-model="form.status">
                  <option value="DRAFT">Draft</option>
                  <option value="PENDING_CANVASS">Pending Canvass</option>
                  <option value="AWARDED">Canvass Awarded</option>
                  <option value="PO_ISSUED">PO Issued</option>
                  <option value="INSPECTED">Inspected &amp; Accepted</option>
                  <option value="VOUCHER_READY">Disbursement Voucher Ready</option>
                  <option value="COMPLETED">Completed</option>
                </select>
              </div>
              <div class="field">
                <label>4. Liquidation Month</label>
                <input v-model="form.liquidation_month" type="text" placeholder="e.g. October 2026" />
              </div>
            </div>

            <div class="form-grid-4">
              <div class="field">
                <label>5. Liquidation Code</label>
                <input v-model="form.liquidation_code" type="text" placeholder="e.g. LIQ-2026-10" />
              </div>
              <div class="field">
                <label>6. ORS / BURS Number</label>
                <input v-model="form.ors_number" type="text" placeholder="e.g. 2026-10-001" />
              </div>
              <div class="field">
                <label>7. ORS / BURS Date</label>
                <div class="date-picker-control" @click="triggerDatePicker($event)">
                  <input v-model="form.ors_date" type="date" />
                  <span class="calendar-icon-btn" title="Open Calendar">📅</span>
                </div>
              </div>
              <div class="field">
                <label>8. ADA Number</label>
                <input v-model="form.ada_number" type="text" placeholder="e.g. ADA-2026-01" />
              </div>
              <div class="field">
                <label>9. ADA Date</label>
                <div class="date-picker-control" @click="triggerDatePicker($event)">
                  <input v-model="form.ada_date" type="date" />
                  <span class="calendar-icon-btn" title="Open Calendar">📅</span>
                </div>
              </div>
            </div>

            <h4 class="sub-heading">Primary Payee / Supplier (Awardee)</h4>
            <div class="form-grid-3">
              <div class="field" :class="{ 'field-has-error': isFieldInvalid('payee_supplier_name') }">
                <div class="flex-between">
                  <label>Supplier / Payee Name * <span v-if="isFieldInvalid('payee_supplier_name')" class="req-star font-bold text-danger">(Required)</span></label>
                  <button type="button" class="btn-link-action" @click="openAddSupplierQuickModal">
                    ➕ New Supplier
                  </button>
                </div>
                <select @change="onSelectSupplier($event.target.value); clearFieldError('payee_supplier_name')">
                  <option value="">-- Choose from Supplier Library --</option>
                  <option
                    v-for="s in getLibraryOptions('SUPPLIER')"
                    :key="s.id"
                    :value="s.name"
                  >
                    {{ s.name }}
                  </option>
                </select>
                <input
                  v-model="form.payee_supplier_name"
                  type="text"
                  placeholder="Or enter custom payee name"
                  class="mt-1"
                  :class="{ 'input-invalid': isFieldInvalid('payee_supplier_name') }"
                  @input="clearFieldError('payee_supplier_name')"
                  required
                />
                <span v-if="isFieldInvalid('payee_supplier_name')" class="error-inline-msg">Payee / Supplier Name is required.</span>
              </div>
              <div class="field">
                <label>TIN / Employee No.</label>
                <input v-model="form.payee_tin" type="text" placeholder="e.g. 123-456-789-000" />
              </div>
              <div class="field">
                <label>Address</label>
                <input v-model="form.payee_address" type="text" placeholder="Full business address" />
              </div>
            </div>

            <div class="form-grid-3">
              <div class="field">
                <label>Cheque Number</label>
                <input v-model="form.cheque_number" type="text" placeholder="e.g. 0001234" />
              </div>
              <div class="field">
                <label>Cheque Date</label>
                <div class="date-picker-control" @click="triggerDatePicker($event)">
                  <input v-model="form.cheque_date" type="date" />
                  <span class="calendar-icon-btn" title="Open Calendar">📅</span>
                </div>
              </div>
            </div>
          </div>

          <!-- TAB 2: Items & Canvass 1, 2, 3 (AOQ) -->
          <div v-show="currentTab === 'ITEMS'" class="form-section">
            <div class="section-title-row">
              <div>
                <h3>Items Specifications &amp; Quotations</h3>
                <p class="section-sub">Enter items requested, item classifications, and compare 3 Canvass Bidders for Abstract of Quotation (AOQ)</p>
              </div>
              <button class="btn-primary btn-sm" @click="addItemRow">
                <span class="btn-icon">➕</span> Add Item
              </button>
            </div>

            <!-- Canvass Suppliers Setup -->
            <h4 class="sub-heading">Canvass Bidders (Abstract of Quotation)</h4>
            <div class="form-grid-3 mb-4">
              <div class="field canvass-box slot-1">
                <label class="font-bold text-accent">Supplier 1 (Awardee / Payee)</label>
                <input v-model="form.payee_supplier_name" type="text" placeholder="Winning bidder / Supplier 1" />
              </div>
              <div class="field canvass-box slot-2">
                <label class="font-bold">Supplier 2 (Canvass 2)</label>
                <select @change="supplier2.supplier_name = $event.target.value" class="mb-1">
                  <option value="">-- Choose from Supplier Library --</option>
                  <option v-for="s in getLibraryOptions('SUPPLIER')" :key="s.id" :value="s.name">
                    {{ s.name }}
                  </option>
                </select>
                <input v-model="supplier2.supplier_name" type="text" placeholder="Supplier 2 Name" />
              </div>
              <div class="field canvass-box slot-3">
                <label class="font-bold">Supplier 3 (Canvass 3)</label>
                <select @change="supplier3.supplier_name = $event.target.value" class="mb-1">
                  <option value="">-- Choose from Supplier Library --</option>
                  <option v-for="s in getLibraryOptions('SUPPLIER')" :key="s.id" :value="s.name">
                    {{ s.name }}
                  </option>
                </select>
                <input v-model="supplier3.supplier_name" type="text" placeholder="Supplier 3 Name" />
              </div>
            </div>

            <!-- Items Table -->
            <div class="table-responsive">
              <table class="data-table">
                <thead>
                  <tr>
                    <th width="45">#</th>
                    <th width="150">Classification</th>
                    <th>Item Description</th>
                    <th width="80">Unit</th>
                    <th width="90">Qty</th>
                    <th width="130">Supplier 1 (₱)</th>
                    <th width="130">Total (₱)</th>
                    <th width="130">Supplier 2 (₱)</th>
                    <th width="130">Supplier 3 (₱)</th>
                    <th width="45"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in form.items" :key="index">
                    <td class="font-bold text-muted">{{ index + 1 }}</td>
                    <td>
                      <input v-model="item.classification" type="text" placeholder="Category" class="table-input" />
                    </td>
                    <td>
                      <input
                        v-model="item.description"
                        type="text"
                        placeholder="Item description *"
                        class="table-input"
                        :class="{ 'input-invalid': isFieldInvalid(`item_desc_${index}`) }"
                        @input="clearFieldError(`item_desc_${index}`)"
                        required
                      />
                    </td>
                    <td>
                      <input v-model="item.unit" type="text" placeholder="pcs" class="table-input" />
                    </td>
                    <td>
                      <input
                        v-model.number="item.quantity"
                        type="number"
                        step="any"
                        class="table-input font-mono"
                        :class="{ 'input-invalid': isFieldInvalid(`item_qty_${index}`) }"
                        @input="recalcItemTotal(item); clearFieldError(`item_qty_${index}`)"
                      />
                    </td>
                    <td>
                      <input
                        v-model.number="item.unit_cost_1"
                        type="number"
                        step="0.01"
                        class="table-input font-mono"
                        :class="{ 'input-invalid': isFieldInvalid(`item_cost_${index}`) }"
                        @input="recalcItemTotal(item); clearFieldError(`item_cost_${index}`)"
                      />
                    </td>
                    <td class="amount-cell font-mono font-bold">
                      ₱{{ formatMoney(item.quantity * item.unit_cost_1) }}
                    </td>
                    <td>
                      <input v-model.number="item.unit_cost_2" type="number" step="0.01" class="table-input font-mono" placeholder="0.00" />
                    </td>
                    <td>
                      <input v-model.number="item.unit_cost_3" type="number" step="0.01" class="table-input font-mono" placeholder="0.00" />
                    </td>
                    <td>
                      <button class="btn-action delete" title="Remove Item" @click="removeItemRow(index)">✕</button>
                    </td>
                  </tr>
                  <tr v-if="!form.items.length">
                    <td colspan="10" class="no-records">No items added yet. Click "+ Add Item" above.</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td colspan="6" class="text-right font-bold">Grand Total (Awarded Canvass 1):</td>
                    <td class="amount-cell font-bold net-due">₱{{ formatMoney(computedGrossAmount) }}</td>
                    <td colspan="3"></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          <!-- TAB 3: Requisition and Issue Slip (RIS - Appendix 63) -->
          <div v-show="currentTab === 'RIS'" class="form-section">
            <div class="section-title-row">
              <div>
                <h3>Appendix 63: Requisition and Issue Slip (RIS)</h3>
                <p class="section-sub">Select verified signatories from libraries or enter official names</p>
              </div>
              <span class="sheet-indicator">RIS</span>
            </div>

            <div class="form-grid-3">
              <div class="field">
                <label>RIS Number</label>
                <input v-model="form.ris_number" type="text" placeholder="e.g. RIS-2026-10" />
              </div>
              <div class="field">
                <label>Requisition Date</label>
                <div class="date-picker-control" @click="triggerDatePicker($event)">
                  <input v-model="form.ris_date1" type="date" />
                  <span class="calendar-icon-btn" title="Open Calendar">📅</span>
                </div>
              </div>
              <div class="field">
                <label>Issue Date</label>
                <div class="date-picker-control" @click="triggerDatePicker($event)">
                  <input v-model="form.ris_date2" type="date" />
                  <span class="calendar-icon-btn" title="Open Calendar">📅</span>
                </div>
              </div>
            </div>

            <div class="field mb-3">
              <label>Purpose</label>
              <textarea v-model="form.ris_purpose" rows="2" placeholder="State purpose of requisition..."></textarea>
            </div>

            <h4 class="sub-heading">Signatories (Dropdown from Libraries)</h4>
            <div class="form-grid-4">
              <div class="field">
                <label>Requested By (Library)</label>
                <select @change="form.ris_requested_by = $event.target.value">
                  <option value="">-- Choose Requested By --</option>
                  <option v-for="p in getLibraryOptions('REQUESTED_BY')" :key="p.id" :value="p.name">
                    {{ p.name }} ({{ p.designation }})
                  </option>
                </select>
                <input v-model="form.ris_requested_by" type="text" class="mt-1" placeholder="Or type name" />
              </div>
              <div class="field">
                <label>Approved By (Library)</label>
                <select @change="form.ris_approved_by = $event.target.value">
                  <option value="">-- Choose Approved By --</option>
                  <option v-for="p in getLibraryOptions('APPROVED_BY')" :key="p.id" :value="p.name">
                    {{ p.name }} ({{ p.designation }})
                  </option>
                </select>
                <input v-model="form.ris_approved_by" type="text" class="mt-1" placeholder="Or type name" />
              </div>
              <div class="field">
                <label>Issued By (Library)</label>
                <select @change="form.ris_issued_by = $event.target.value">
                  <option value="">-- Choose Issued By --</option>
                  <option v-for="p in getLibraryOptions('ISSUED_BY')" :key="p.id" :value="p.name">
                    {{ p.name }} ({{ p.designation }})
                  </option>
                </select>
                <input v-model="form.ris_issued_by" type="text" class="mt-1" placeholder="Or type name" />
              </div>
              <div class="field">
                <label>Received By (Library)</label>
                <select @change="form.ris_received_by = $event.target.value">
                  <option value="">-- Choose Received By --</option>
                  <option v-for="p in getLibraryOptions('RECEIVED_BY')" :key="p.id" :value="p.name">
                    {{ p.name }} ({{ p.designation }})
                  </option>
                </select>
                <input v-model="form.ris_received_by" type="text" class="mt-1" placeholder="Or type name" />
              </div>
            </div>

            <!-- RIS Items Table (Appendix 63 • Sheet 'RIS') -->
            <div class="table-header-action mt-4">
              <div>
                <h4 class="sub-heading mb-0">Requisition and Issue Slip Items (Sheet 'RIS' • Appendix 63)</h4>
                <p class="section-sub">Items requisitioned and stock availability. Changes are synchronized across PR, PO, and AOQ.</p>
              </div>
              <button type="button" class="btn-primary btn-sm" @click="addItemRow">
                <span class="btn-icon">➕</span> Add Item to RIS
              </button>
            </div>

            <div class="table-responsive mt-2">
              <table class="data-table">
                <thead>
                  <tr>
                    <th width="80">Stock No.</th>
                    <th width="100">Unit</th>
                    <th>Item Description</th>
                    <th width="110">Qty Requested</th>
                    <th width="110">Stock Available?</th>
                    <th width="110">Qty Issued</th>
                    <th width="45"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in form.items" :key="index">
                    <td>
                      <input v-model="item.item_code" type="text" placeholder="1" class="table-input font-mono" />
                    </td>
                    <td>
                      <input v-model="item.unit" type="text" placeholder="pcs" class="table-input" />
                    </td>
                    <td>
                      <input
                        v-model="item.description"
                        type="text"
                        placeholder="Item description *"
                        class="table-input"
                        :class="{ 'input-invalid': isFieldInvalid(`item_desc_${index}`) }"
                        @input="clearFieldError(`item_desc_${index}`)"
                        required
                      />
                    </td>
                    <td>
                      <input
                        v-model.number="item.quantity"
                        type="number"
                        step="any"
                        class="table-input font-mono"
                        :class="{ 'input-invalid': isFieldInvalid(`item_qty_${index}`) }"
                        @input="recalcItemTotal(item); clearFieldError(`item_qty_${index}`)"
                      />
                    </td>
                    <td class="text-center font-bold text-success">
                      ✓ Yes
                    </td>
                    <td>
                      <input
                        v-model.number="item.quantity"
                        type="number"
                        step="any"
                        class="table-input font-mono"
                      />
                    </td>
                    <td>
                      <button type="button" class="btn-action delete" title="Remove Item" @click="removeItemRow(index)">✕</button>
                    </td>
                  </tr>
                  <tr v-if="!form.items.length">
                    <td colspan="7" class="no-records">No items in RIS. Click "+ Add Item to RIS" above.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- TAB 4: Purchase Request (PR - Appendix 60) -->
          <div v-show="currentTab === 'PR'" class="form-section">
            <div class="section-title-row">
              <div>
                <h3>Appendix 60: Purchase Request (PR)</h3>
                <p class="section-sub">Standard DepEd Purchase Request Appendix 60 (Sheet 'PR-A&amp;m' in BLANK.xlsx)</p>
              </div>
              <span class="sheet-indicator">PR-A&amp;m</span>
            </div>

            <div class="form-grid-3">
              <div class="field">
                <label>PR Number</label>
                <input v-model="form.pr_number" type="text" placeholder="e.g. PR-2026-10" />
              </div>
              <div class="field">
                <label>PR Date</label>
                <div class="date-picker-control" @click="triggerDatePicker($event)">
                  <input v-model="form.pr_date" type="date" />
                  <span class="calendar-icon-btn" title="Open Calendar">📅</span>
                </div>
              </div>
            </div>

            <div class="field mb-3">
              <label>Purchase Request Purpose</label>
              <textarea v-model="form.pr_purpose" rows="2" placeholder="Purchase request purpose..."></textarea>
            </div>

            <h4 class="sub-heading">PR Signatories</h4>
            <div class="form-grid-2">
              <div class="field">
                <label>Requested By (Library)</label>
                <select @change="form.pr_requested_by = $event.target.value">
                  <option value="">-- Choose Requested By --</option>
                  <option v-for="p in getLibraryOptions('REQUESTED_BY')" :key="p.id" :value="p.name">
                    {{ p.name }} ({{ p.designation }})
                  </option>
                </select>
                <input v-model="form.pr_requested_by" type="text" class="mt-1" />
              </div>
              <div class="field">
                <label>Approved By (Library)</label>
                <select @change="form.pr_approved_by = $event.target.value">
                  <option value="">-- Choose Approved By --</option>
                  <option v-for="p in getLibraryOptions('APPROVED_BY')" :key="p.id" :value="p.name">
                    {{ p.name }} ({{ p.designation }})
                  </option>
                </select>
                <input v-model="form.pr_approved_by" type="text" class="mt-1" />
              </div>
            </div>

            <!-- PR Items Entry Table (Appendix 60 • Sheet 'PR-A&m') -->
            <div class="table-header-action mt-4">
              <div>
                <h4 class="sub-heading mb-0">Purchase Request Items (Sheet 'PR-A&amp;m' • Appendix 60)</h4>
                <p class="section-sub">Enter stock property number, unit, description, quantity, and estimated cost. Linked directly to BLANK.xlsx PR-A&amp;m.</p>
              </div>
              <button type="button" class="btn-primary btn-sm" @click="addItemRow">
                <span class="btn-icon">➕</span> Add Item to PR
              </button>
            </div>

            <div class="table-responsive mt-2">
              <table class="data-table">
                <thead>
                  <tr>
                    <th width="60">Item #</th>
                    <th width="120">Stock / Prop No.</th>
                    <th width="90">Unit</th>
                    <th>Item Description</th>
                    <th width="100">Quantity</th>
                    <th width="130">Estimated Cost (₱)</th>
                    <th width="140">Total Cost (₱)</th>
                    <th width="45"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in form.items" :key="index">
                    <td class="font-bold text-muted">{{ index + 1 }}</td>
                    <td>
                      <input v-model="item.item_code" type="text" placeholder="1" class="table-input font-mono" />
                    </td>
                    <td>
                      <input v-model="item.unit" type="text" placeholder="pcs" class="table-input" />
                    </td>
                    <td>
                      <input
                        v-model="item.description"
                        type="text"
                        placeholder="Item description *"
                        class="table-input"
                        :class="{ 'input-invalid': isFieldInvalid(`item_desc_${index}`) }"
                        @input="clearFieldError(`item_desc_${index}`)"
                        required
                      />
                    </td>
                    <td>
                      <input
                        v-model.number="item.quantity"
                        type="number"
                        step="any"
                        class="table-input font-mono"
                        :class="{ 'input-invalid': isFieldInvalid(`item_qty_${index}`) }"
                        @input="recalcItemTotal(item); clearFieldError(`item_qty_${index}`)"
                      />
                    </td>
                    <td>
                      <input
                        v-model.number="item.unit_cost_1"
                        type="number"
                        step="0.01"
                        class="table-input font-mono"
                        :class="{ 'input-invalid': isFieldInvalid(`item_cost_${index}`) }"
                        @input="recalcItemTotal(item); clearFieldError(`item_cost_${index}`)"
                      />
                    </td>
                    <td class="amount-cell font-mono font-bold">
                      ₱{{ formatMoney(item.quantity * item.unit_cost_1) }}
                    </td>
                    <td>
                      <button type="button" class="btn-action delete" title="Remove Item" @click="removeItemRow(index)">✕</button>
                    </td>
                  </tr>
                  <tr v-if="!form.items.length">
                    <td colspan="8" class="no-records">No items in Purchase Request. Click "+ Add Item to PR" above.</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td colspan="6" class="text-right font-bold">Total Estimated Cost (PR-A&amp;m):</td>
                    <td class="amount-cell font-bold net-due">₱{{ formatMoney(computedGrossAmount) }}</td>
                    <td></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          <!-- TAB 5: Purchase Order (PO - Appendix 61) -->
          <div v-show="currentTab === 'PO'" class="form-section">
            <div class="section-title-row">
              <div>
                <h3>Appendix 61: Purchase Order (PO)</h3>
                <p class="section-sub">Procurement Terms and Conditions (Sheet 'PO' in BLANK.xlsx)</p>
              </div>
              <span class="sheet-indicator">PO</span>
            </div>

            <div class="form-grid-3">
              <div class="field">
                <label>PO Number</label>
                <input v-model="form.po_number" type="text" placeholder="e.g. 2026-04" />
              </div>
              <div class="field">
                <label>PO Date</label>
                <div class="date-picker-control" @click="triggerDatePicker($event)">
                  <input v-model="form.po_date" type="date" />
                  <span class="calendar-icon-btn" title="Open Calendar">📅</span>
                </div>
              </div>
              <div class="field">
                <label>Place of Delivery</label>
                <input v-model="form.po_place_of_delivery" type="text" />
              </div>
            </div>

            <h4 class="sub-heading">Procurement Terms (From Libraries)</h4>
            <div class="form-grid-3">
              <div class="field">
                <label>Mode of Procurement</label>
                <select @change="form.po_mode_of_procurement = $event.target.value">
                  <option value="">-- Choose Mode of Procurement --</option>
                  <option v-for="m in getLibraryOptions('MODE_OF_PROCUREMENT')" :key="m.id" :value="m.name">
                    {{ m.name }}
                  </option>
                </select>
                <input v-model="form.po_mode_of_procurement" type="text" class="mt-1" />
              </div>
              <div class="field">
                <label>Delivery Term</label>
                <select @change="form.po_delivery_term = $event.target.value">
                  <option value="">-- Choose Delivery Term --</option>
                  <option v-for="d in getLibraryOptions('DELIVERY_TERM')" :key="d.id" :value="d.name">
                    {{ d.name }}
                  </option>
                </select>
                <input v-model="form.po_delivery_term" type="text" class="mt-1" />
              </div>
              <div class="field">
                <label>Payment Term</label>
                <select @change="form.po_payment_term = $event.target.value">
                  <option value="">-- Choose Payment Term --</option>
                  <option v-for="p in getLibraryOptions('PAYMENT_TERM')" :key="p.id" :value="p.name">
                    {{ p.name }}
                  </option>
                </select>
                <input v-model="form.po_payment_term" type="text" class="mt-1" />
              </div>
            </div>

            <!-- PO Items Entry Table (Appendix 61 • Sheet 'PO') -->
            <div class="table-header-action mt-4">
              <div>
                <h4 class="sub-heading mb-0">Purchase Order Ordered Items (Sheet 'PO' • Appendix 61)</h4>
                <p class="section-sub">Furnish items, quantities, agreed unit price, and total amount. Linked to winning supplier {{ form.payee_supplier_name || 'Awardee' }}.</p>
              </div>
              <button type="button" class="btn-primary btn-sm" @click="addItemRow">
                <span class="btn-icon">➕</span> Add Item to PO
              </button>
            </div>

            <div class="table-responsive mt-2">
              <table class="data-table">
                <thead>
                  <tr>
                    <th width="80">Stock No.</th>
                    <th width="90">Unit</th>
                    <th>Description</th>
                    <th width="100">Quantity</th>
                    <th width="130">Unit Cost (₱)</th>
                    <th width="140">Amount (₱)</th>
                    <th width="45"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in form.items" :key="index">
                    <td>
                      <input v-model="item.item_code" type="text" placeholder="1" class="table-input font-mono" />
                    </td>
                    <td>
                      <input v-model="item.unit" type="text" placeholder="pcs" class="table-input" />
                    </td>
                    <td>
                      <input
                        v-model="item.description"
                        type="text"
                        placeholder="Item description *"
                        class="table-input"
                        :class="{ 'input-invalid': isFieldInvalid(`item_desc_${index}`) }"
                        @input="clearFieldError(`item_desc_${index}`)"
                        required
                      />
                    </td>
                    <td>
                      <input
                        v-model.number="item.quantity"
                        type="number"
                        step="any"
                        class="table-input font-mono"
                        :class="{ 'input-invalid': isFieldInvalid(`item_qty_${index}`) }"
                        @input="recalcItemTotal(item); clearFieldError(`item_qty_${index}`)"
                      />
                    </td>
                    <td>
                      <input
                        v-model.number="item.unit_cost_1"
                        type="number"
                        step="0.01"
                        class="table-input font-mono"
                        :class="{ 'input-invalid': isFieldInvalid(`item_cost_${index}`) }"
                        @input="recalcItemTotal(item); clearFieldError(`item_cost_${index}`)"
                      />
                    </td>
                    <td class="amount-cell font-mono font-bold">
                      ₱{{ formatMoney(item.quantity * item.unit_cost_1) }}
                    </td>
                    <td>
                      <button type="button" class="btn-action delete" title="Remove Item" @click="removeItemRow(index)">✕</button>
                    </td>
                  </tr>
                  <tr v-if="!form.items.length">
                    <td colspan="7" class="no-records">No items in Purchase Order. Click "+ Add Item to PO" above.</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td colspan="5" class="text-right font-bold">Total Purchase Order Amount (PO):</td>
                    <td class="amount-cell font-bold net-due">₱{{ formatMoney(computedGrossAmount) }}</td>
                    <td></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          <!-- TAB 6: Inspection & Acceptance Report (IAR - Appendix 62) -->
          <div v-show="currentTab === 'IAR'" class="form-section">
            <div class="section-title-row">
              <div>
                <h3>Appendix 62: Inspection &amp; Acceptance Report (IAR)</h3>
                <p class="section-sub">Inspection verification and Property Custodian acceptance (Sheet 'IAR' in BLANK.xlsx)</p>
              </div>
              <span class="sheet-indicator">IAR</span>
            </div>

            <div class="form-grid-4">
              <div class="field">
                <label>IAR Number</label>
                <input v-model="form.iar_number" type="text" placeholder="e.g. IAR-2026-10" />
              </div>
              <div class="field">
                <label>IAR Date</label>
                <div class="date-picker-control" @click="triggerDatePicker($event)">
                  <input v-model="form.iar_date" type="date" />
                  <span class="calendar-icon-btn" title="Open Calendar">📅</span>
                </div>
              </div>
              <div class="field">
                <label>Invoice / Sales Receipt No.</label>
                <input v-model="form.iar_invoice_number" type="text" />
              </div>
              <div class="field">
                <label>Invoice Date</label>
                <div class="date-picker-control" @click="triggerDatePicker($event)">
                  <input v-model="form.iar_invoice_date" type="date" />
                  <span class="calendar-icon-btn" title="Open Calendar">📅</span>
                </div>
              </div>
            </div>

            <h4 class="sub-heading">Inspection Signatories</h4>
            <div class="form-grid-2">
              <div class="field">
                <label>Inspection Officer (Library)</label>
                <select @change="form.iar_inspection_officer = $event.target.value">
                  <option value="">-- Choose Signatory --</option>
                  <option v-for="p in getLibraryOptions('RECEIVED_BY')" :key="p.id" :value="p.name">
                    {{ p.name }} ({{ p.designation }})
                  </option>
                </select>
                <input v-model="form.iar_inspection_officer" type="text" class="mt-1" />
              </div>
              <div class="field">
                <label>Property Custodian (Library)</label>
                <select @change="form.iar_property_custodian = $event.target.value">
                  <option value="">-- Choose Signatory --</option>
                  <option v-for="p in getLibraryOptions('REQUESTED_BY')" :key="p.id" :value="p.name">
                    {{ p.name }} ({{ p.designation }})
                  </option>
                </select>
                <input v-model="form.iar_property_custodian" type="text" class="mt-1" />
              </div>
            </div>

            <!-- IAR Items Table (Appendix 62 • Sheet 'IAR') -->
            <div class="table-header-action mt-4">
              <div>
                <h4 class="sub-heading mb-0">Inspected &amp; Accepted Items (Sheet 'IAR' • Appendix 62)</h4>
                <p class="section-sub">Verification of delivered articles received per PO and Invoice. Linked directly to BLANK.xlsx IAR.</p>
              </div>
              <button type="button" class="btn-primary btn-sm" @click="addItemRow">
                <span class="btn-icon">➕</span> Add Item
              </button>
            </div>

            <div class="table-responsive mt-2">
              <table class="data-table">
                <thead>
                  <tr>
                    <th width="120">Stock / Prop No.</th>
                    <th>Description</th>
                    <th width="90">Unit</th>
                    <th width="110">Quantity</th>
                    <th width="160">Inspection Status</th>
                    <th width="45"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in form.items" :key="index">
                    <td>
                      <input v-model="item.item_code" type="text" placeholder="1" class="table-input font-mono" />
                    </td>
                    <td>
                      <input
                        v-model="item.description"
                        type="text"
                        placeholder="Item description *"
                        class="table-input"
                        :class="{ 'input-invalid': isFieldInvalid(`item_desc_${index}`) }"
                        @input="clearFieldError(`item_desc_${index}`)"
                        required
                      />
                    </td>
                    <td>
                      <input v-model="item.unit" type="text" placeholder="pcs" class="table-input" />
                    </td>
                    <td>
                      <input
                        v-model.number="item.quantity"
                        type="number"
                        step="any"
                        class="table-input font-mono"
                        :class="{ 'input-invalid': isFieldInvalid(`item_qty_${index}`) }"
                        @input="recalcItemTotal(item); clearFieldError(`item_qty_${index}`)"
                      />
                    </td>
                    <td>
                      <span class="badge status-badge">✓ Accepted &amp; Verified</span>
                    </td>
                    <td>
                      <button type="button" class="btn-action delete" title="Remove Item" @click="removeItemRow(index)">✕</button>
                    </td>
                  </tr>
                  <tr v-if="!form.items.length">
                    <td colspan="6" class="no-records">No items recorded for inspection. Click "+ Add Item" above.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- TAB 7: Disbursement Voucher (DV) & Tax Breakdown -->
          <div v-show="currentTab === 'DV'" class="form-section">
            <div class="section-title-row">
              <div>
                <h3>Disbursement Voucher (DV) &amp; Tax Deductions</h3>
                <p class="section-sub">Automatic computation for Percent 1 (5%), Percent 2 (1%), and Net Amount Due</p>
              </div>
              <span class="sheet-indicator">DV</span>
            </div>

            <div class="form-grid-3">
              <div class="field">
                <label>DV Number</label>
                <input v-model="form.dv_number" type="text" placeholder="e.g. 2026-10-001" />
              </div>
              <div class="field">
                <label>DV Date</label>
                <div class="date-picker-control" @click="triggerDatePicker($event)">
                  <input v-model="form.dv_date" type="date" />
                  <span class="calendar-icon-btn" title="Open Calendar">📅</span>
                </div>
              </div>
              <div class="field">
                <label>Mode of Payment</label>
                <select v-model="form.dv_mode_of_payment">
                  <option value="MDSCheck">MDSCheck</option>
                  <option value="Commercial Check">Commercial Check</option>
                  <option value="ADA">ADA</option>
                  <option value="Others">Others</option>
                </select>
              </div>
            </div>

            <!-- Tax Computation Cards -->
            <div class="dv-computation-card glass-panel">
              <div class="dv-calc-row">
                <span class="calc-label font-bold">GROSS AMOUNT:</span>
                <span class="calc-val font-mono font-bold">₱{{ formatMoney(computedGrossAmount) }}</span>
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
                <span class="calc-val font-mono text-danger">- ₱{{ formatMoney(computedTax1) }}</span>
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
                <span class="calc-val font-mono text-danger">- ₱{{ formatMoney(computedTax2) }}</span>
              </div>
              <div class="dv-calc-row total-tax-row">
                <span class="calc-label font-medium">Total Withholding Deductions:</span>
                <span class="calc-val font-mono text-danger">- ₱{{ formatMoney(computedTax1 + computedTax2) }}</span>
              </div>
              <div class="dv-calc-row due-row">
                <span class="calc-label font-bold text-accent">NET AMOUNT DUE:</span>
                <span class="calc-val due-val font-mono">₱{{ formatMoney(computedNetAmount) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer Bar -->
        <div class="modal-footer glass-panel">
          <div class="footer-summary">
            Gross: <strong>₱{{ formatMoney(computedGrossAmount) }}</strong> | Total Deductions: <strong class="text-danger">-₱{{ formatMoney(computedTax1 + computedTax2) }}</strong> | Net Due: <strong class="text-accent">₱{{ formatMoney(computedNetAmount) }}</strong>
          </div>
          <div class="footer-btns">
            <button class="btn-secondary" @click="closeModal">Cancel</button>
            <button class="btn-primary" :disabled="saving" @click="saveVoucher">
              {{ saving ? 'Saving...' : (isEditing ? 'Update Voucher' : 'Create Voucher') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- MODAL: ADD / EDIT LIBRARY ITEM -->
    <!-- ========================================================================= -->
    <div v-if="showLibModal" class="modal-overlay" @click.self="showLibModal = false">
      <div class="modal-content glass-panel modal-medium">
        <div class="modal-header">
          <h3>{{ isEditingLib ? 'Edit' : 'Add New' }} {{ currentLibCategoryLabel }}</h3>
          <button class="btn-close" @click="showLibModal = false">✕</button>
        </div>
        <div v-if="libValidationErrors.length > 0" class="validation-banner mb-3">
          <div class="banner-icon">⚠️</div>
          <div class="banner-content">
            <strong>Missing required information:</strong>
            <ul>
              <li v-for="(err, idx) in libValidationErrors" :key="idx">{{ err.message }}</li>
            </ul>
          </div>
          <button class="btn-clear-errors" @click="libValidationErrors = []" title="Dismiss error banner">✕</button>
        </div>

        <div class="modal-body">
          <div class="field mb-3">
            <label>Library Category</label>
            <select v-model="libForm.category" :disabled="isEditingLib">
              <option v-for="cat in libraryCategories" :key="cat.key" :value="cat.key">
                {{ cat.label }}
              </option>
            </select>
          </div>

          <div class="field mb-3" :class="{ 'field-has-error': isLibFieldInvalid('name') }">
            <label>{{ libForm.category === 'SUPPLIER' ? 'Supplier / Company / Payee Name *' : 'Name / Title *' }} <span v-if="isLibFieldInvalid('name')" class="req-star font-bold text-danger">(Required)</span></label>
            <input
              v-model="libForm.name"
              type="text"
              :placeholder="libForm.category === 'SUPPLIER' ? 'e.g. Vicky\'s Hardware' : 'Enter name or title'"
              :class="{ 'input-invalid': isLibFieldInvalid('name') }"
              @input="clearLibFieldError('name')"
              required
            />
            <span v-if="isLibFieldInvalid('name')" class="error-inline-msg">{{ libForm.category === 'SUPPLIER' ? 'Supplier name' : 'Name / title' }} is required.</span>
          </div>

          <div v-if="libForm.category === 'TRANSACTION_TYPE'" class="field mb-3">
            <label>Transaction Code</label>
            <input v-model="libForm.code" type="text" placeholder="e.g. SUPPLIES, REPAIR" />
          </div>

          <div v-if="libForm.category === 'SUPPLIER'" class="form-grid-2 mb-3">
            <div class="field">
              <label>Business Address</label>
              <input v-model="libForm.address" type="text" placeholder="e.g. Centro, Lal-lo, Cagayan" />
            </div>
            <div class="field">
              <label>TIN Number</label>
              <input v-model="libForm.tin" type="text" placeholder="e.g. 123-456-789-000" />
            </div>
          </div>

          <div v-if="['REQUESTED_BY', 'APPROVED_BY', 'ISSUED_BY', 'RECEIVED_BY'].includes(libForm.category)" class="field mb-3">
            <label>Designation / Position</label>
            <input v-model="libForm.designation" type="text" placeholder="e.g. Principal II, Property Custodian" />
          </div>

          <div class="form-grid-2 mb-3">
            <div class="field">
              <label>Sort Order</label>
              <input v-model.number="libForm.sort_order" type="number" />
            </div>
            <div class="field">
              <label>Status</label>
              <select v-model="libForm.is_active">
                <option :value="true">Active</option>
                <option :value="false">Inactive</option>
              </select>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showLibModal = false">Cancel</button>
          <button class="btn-primary" @click="saveLibraryItem">Save Item</button>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- MODAL: PDF PREVIEW MODAL -->
    <!-- ========================================================================= -->
    <!-- ========================================================================= -->
    <!-- MODAL: PDF PREVIEW MODAL -->
    <!-- ========================================================================= -->
    <div v-if="showPdfModal" class="modal-overlay" @click.self="closePdfPreview">
      <div class="modal-content glass-panel modal-pdf-preview">
        <div class="modal-header">
          <div class="header-left">
            <h3>📄 Official Forms PDF Preview: {{ previewTransCode }}</h3>
            <p class="modal-subtitle">Fast Template Preview &amp; Official Appendix Form Generation</p>
          </div>
          <div class="header-right">
            <button class="btn-primary mr-2" @click="downloadCurrentPdf">
              📥 Download {{ previewSheet === 'ALL' ? 'All Appendices PDF' : (previewSheet + ' PDF') }}
            </button>
            <button class="btn-secondary mr-2" @click="store.downloadExcel(previewVoucherId, previewTransCode)">
              📊 Download Excel (.xlsx)
            </button>
            <button class="btn-close" @click="closePdfPreview">✕</button>
          </div>
        </div>

        <!-- Sheet Selector Tabs Bar for Fast Instant Form Switching -->
        <div class="pdf-sheet-bar glass-panel">
          <button
            v-for="s in previewSheetsList"
            :key="s.key"
            class="pdf-sheet-btn"
            :class="{ active: previewSheet === s.key }"
            @click="changePreviewSheet(s.key)"
          >
            <span>{{ s.icon }}</span> {{ s.label }}
          </button>
        </div>

        <div class="modal-body pdf-body">
          <div v-if="pdfLoading" class="loading-state">
            <div class="spinner"></div>
            <p>Rendering {{ currentSheetLabel }} from official Excel template...</p>
          </div>
          <div v-else-if="pdfError" class="empty-state">
            <div class="empty-icon">⚠️</div>
            <h3>PDF Preview Notice</h3>
            <p>{{ pdfError }}</p>
            <button class="btn-primary mt-3" @click="store.downloadExcel(previewVoucherId, previewTransCode)">
              📥 Download Excel Instead
            </button>
          </div>
          <iframe
            v-else-if="pdfUrl"
            :src="pdfUrl"
            class="pdf-iframe"
            title="Voucher Appendix PDF Preview"
          ></iframe>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- VIEW 4: SUMMARY REPORTING MODAL -->
    <!-- ========================================================================= -->
    <div v-if="showReportModal" class="modal-overlay" @click.self="showReportModal = false">
      <div class="modal-fullscreen report-modal glass-panel">
        <div class="modal-header">
          <div class="report-header-title">
            <div class="modal-title-row">
              <span class="report-icon">📊</span>
              <div>
                <h3>Voucher Expenditure &amp; Procurement Summary Reports</h3>
                <p class="subtitle">
                  Real-time analytics and distribution breakdown for {{ filteredTransactions.length }} filtered transaction(s)
                </p>
              </div>
            </div>
          </div>
          <div class="report-header-actions">
            <button class="btn-secondary" @click="printSummaryReport">
              🖨️ Print / Save Report
            </button>
            <button class="btn-close" @click="showReportModal = false">✕</button>
          </div>
        </div>

        <!-- Report Tabs Navigation -->
        <div class="report-tabs-bar">
          <button
            class="report-tab-btn"
            :class="{ active: reportActiveTab === 'BY_TYPE' }"
            @click="reportActiveTab = 'BY_TYPE'"
          >
            🏷️ Summary by Transaction Type
          </button>
          <button
            class="report-tab-btn"
            :class="{ active: reportActiveTab === 'BY_PAYEE' }"
            @click="reportActiveTab = 'BY_PAYEE'"
          >
            🏢 Summary by Payee / Supplier
          </button>
          <button
            class="report-tab-btn"
            :class="{ active: reportActiveTab === 'BY_ITEM' }"
            @click="reportActiveTab = 'BY_ITEM'"
          >
            📦 Summary by Items &amp; Materials
          </button>
        </div>

        <!-- Report Content Area -->
        <div class="modal-body report-body printable-report" id="printableReportArea">
          <!-- Filter Scope Banner -->
          <div class="report-scope-banner">
            <div class="scope-item">
              <span class="scope-lbl">Date Scope:</span>
              <strong>{{ dateFrom || dateTo ? `${dateFrom || 'Start'} to ${dateTo || 'End'} (${dateFilterField})` : 'All Dates Recorded' }}</strong>
            </div>
            <div class="scope-item">
              <span class="scope-lbl">Type Scope:</span>
              <strong>{{ filterType === 'ALL' ? 'All Types' : filterType }}</strong>
            </div>
            <div class="scope-item">
              <span class="scope-lbl">Status Scope:</span>
              <strong>{{ filterStatus === 'ALL' ? 'All Statuses' : filterStatus }}</strong>
            </div>
            <div class="scope-item">
              <span class="scope-lbl">Total Filtered Spend:</span>
              <strong class="text-royal">₱ {{ formatMoney(summaryTotalSpend) }}</strong>
            </div>
          </div>

          <!-- TAB 1: SUMMARY BY TRANSACTION TYPE -->
          <div v-if="reportActiveTab === 'BY_TYPE'" class="report-section">
            <div class="report-cards-summary">
              <div
                v-for="item in reportByTypeData"
                :key="item.type"
                class="report-stat-card"
              >
                <div class="stat-type-label">{{ item.label }}</div>
                <div class="stat-amount">₱ {{ formatMoney(item.totalAmount) }}</div>
                <div class="stat-meta">
                  <span>{{ item.count }} Transaction(s)</span>
                  <span>{{ item.percent.toFixed(1) }}% of Total</span>
                </div>
                <div class="stat-progress-bar">
                  <div class="stat-progress-fill" :style="{ width: `${item.percent}%` }"></div>
                </div>
              </div>
            </div>

            <div class="report-table-box mt-4">
              <table class="report-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Transaction Type</th>
                    <th class="text-center">Count</th>
                    <th class="text-right">Total Amount (₱)</th>
                    <th class="text-right">Average / Voucher (₱)</th>
                    <th class="text-right">Share (%)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, idx) in reportByTypeData" :key="item.type">
                    <td>{{ idx + 1 }}</td>
                    <td>
                      <span class="type-badge">{{ item.label }}</span>
                    </td>
                    <td class="text-center font-bold">{{ item.count }}</td>
                    <td class="text-right font-mono font-bold">₱ {{ formatMoney(item.totalAmount) }}</td>
                    <td class="text-right font-mono">₱ {{ formatMoney(item.count > 0 ? item.totalAmount / item.count : 0) }}</td>
                    <td class="text-right font-bold text-royal">{{ item.percent.toFixed(1) }}%</td>
                  </tr>
                  <tr class="report-total-row">
                    <td colspan="2">TOTAL</td>
                    <td class="text-center font-bold">{{ filteredTransactions.length }}</td>
                    <td class="text-right font-mono font-bold text-royal">₱ {{ formatMoney(summaryTotalSpend) }}</td>
                    <td class="text-right font-mono">₱ {{ formatMoney(filteredTransactions.length ? summaryTotalSpend / filteredTransactions.length : 0) }}</td>
                    <td class="text-right font-bold text-royal">100.0%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- TAB 2: SUMMARY BY PAYEE / SUPPLIER -->
          <div v-if="reportActiveTab === 'BY_PAYEE'" class="report-section">
            <div class="report-table-box">
              <div class="report-box-header">
                <h4>🏢 Payee &amp; Supplier Procurement Distribution ({{ reportByPayeeData.length }} Payees)</h4>
              </div>
              <div v-if="reportByPayeeData.length === 0" class="empty-state py-4">
                <p>No payees or suppliers found for the current filtered scope.</p>
              </div>
              <table v-else class="report-table">
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Payee / Supplier Name</th>
                    <th class="text-center">Vouchers Count</th>
                    <th class="text-right">Total Disbursed (₱)</th>
                    <th class="text-right">Share of Total</th>
                    <th>Spend Share Graph</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(p, idx) in reportByPayeeData" :key="p.name">
                    <td>
                      <span class="rank-badge" :class="{ 'top-rank': idx < 3 }">{{ idx + 1 }}</span>
                    </td>
                    <td>
                      <div class="font-bold text-primary">{{ p.name }}</div>
                      <div v-if="p.address" class="sub-info">{{ p.address }}</div>
                    </td>
                    <td class="text-center font-bold">{{ p.count }}</td>
                    <td class="text-right font-mono font-bold text-royal">₱ {{ formatMoney(p.totalAmount) }}</td>
                    <td class="text-right font-bold">{{ p.percent.toFixed(1) }}%</td>
                    <td style="min-width: 140px;">
                      <div class="stat-progress-bar">
                        <div class="stat-progress-fill" :style="{ width: `${p.percent}%` }"></div>
                      </div>
                    </td>
                  </tr>
                  <tr class="report-total-row">
                    <td colspan="2">TOTAL</td>
                    <td class="text-center font-bold">{{ filteredTransactions.length }}</td>
                    <td class="text-right font-mono font-bold text-royal">₱ {{ formatMoney(summaryTotalSpend) }}</td>
                    <td class="text-right font-bold text-royal">100.0%</td>
                    <td></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- TAB 3: SUMMARY BY ITEMS & MATERIALS -->
          <div v-if="reportActiveTab === 'BY_ITEM'" class="report-section">
            <div class="report-table-box">
              <div class="report-box-header">
                <h4>📦 Itemized Material &amp; Supply Procurements ({{ reportByItemData.length }} Unique Items)</h4>
              </div>
              <div v-if="reportByItemData.length === 0" class="empty-state py-4">
                <p>No items registered under the current filtered vouchers.</p>
              </div>
              <table v-else class="report-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Item Description</th>
                    <th>Unit</th>
                    <th class="text-center">Total Qty Purchased</th>
                    <th class="text-right">Avg Unit Cost (₱)</th>
                    <th class="text-right">Total Expenditure (₱)</th>
                    <th class="text-right">Spend Share</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(it, idx) in reportByItemData" :key="it.description">
                    <td>{{ idx + 1 }}</td>
                    <td>
                      <span class="font-bold text-primary">{{ it.description }}</span>
                    </td>
                    <td>
                      <span class="badge-count">{{ it.unit || 'unit' }}</span>
                    </td>
                    <td class="text-center font-bold">{{ it.totalQty }}</td>
                    <td class="text-right font-mono">₱ {{ formatMoney(it.avgUnitCost) }}</td>
                    <td class="text-right font-mono font-bold text-royal">₱ {{ formatMoney(it.totalCost) }}</td>
                    <td class="text-right font-bold">{{ it.percent.toFixed(1) }}%</td>
                  </tr>
                  <tr class="report-total-row">
                    <td colspan="3">TOTAL ITEMIZED EXPENDITURE</td>
                    <td class="text-center font-bold">{{ reportItemsTotalQty }}</td>
                    <td></td>
                    <td class="text-right font-mono font-bold text-royal">₱ {{ formatMoney(reportItemsTotalCost) }}</td>
                    <td class="text-right font-bold text-royal">100.0%</td>
                  </tr>
                </tbody>
              </table>
            </div>
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

const currentView = ref('TRANSACTIONS') // 'TRANSACTIONS' or 'LIBRARIES'
const searchQuery = ref('')
const filterType = ref('ALL')
const filterStatus = ref('ALL')

// Date Filter State
const dateFilterField = ref('created_at')
const dateFrom = ref('')
const dateTo = ref('')
const activeDatePreset = ref('ALL')

const applyDatePreset = (preset) => {
  activeDatePreset.value = preset
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth() // 0-indexed

  const formatYMD = (d) => {
    const y = d.getFullYear()
    const m = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return `${y}-${m}-${day}`
  }

  if (preset === 'ALL') {
    dateFrom.value = ''
    dateTo.value = ''
  } else if (preset === 'THIS_MONTH') {
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    dateFrom.value = formatYMD(firstDay)
    dateTo.value = formatYMD(lastDay)
  } else if (preset === 'LAST_30') {
    const past = new Date()
    past.setDate(past.getDate() - 30)
    dateFrom.value = formatYMD(past)
    dateTo.value = formatYMD(now)
  } else if (preset === 'THIS_QUARTER') {
    const qQuarter = Math.floor(month / 3)
    const firstDay = new Date(year, qQuarter * 3, 1)
    const lastDay = new Date(year, (qQuarter + 1) * 3, 0)
    dateFrom.value = formatYMD(firstDay)
    dateTo.value = formatYMD(lastDay)
  } else if (preset === 'THIS_YEAR') {
    dateFrom.value = `${year}-01-01`
    dateTo.value = `${year}-12-31`
  }
}

const clearDateFilter = () => {
  dateFrom.value = ''
  dateTo.value = ''
  activeDatePreset.value = 'ALL'
}

// Summary Reporting Modal State
const showReportModal = ref(false)
const reportActiveTab = ref('BY_TYPE') // 'BY_TYPE', 'BY_PAYEE', 'BY_ITEM'

const openSummaryReportModal = () => {
  showReportModal.value = true
}

const printSummaryReport = () => {
  window.print()
}

// PDF Preview Modal State
const showPdfModal = ref(false)
const pdfLoading = ref(false)
const pdfError = ref(null)
const pdfUrl = ref(null)
const previewVoucherId = ref(null)
const previewTransCode = ref('')
const previewSheet = ref('DV')
const pdfCache = ref(new Map())

const previewSheetsList = [
  { key: 'DV', label: 'Disbursement Voucher (DV)', icon: '💵' },
  { key: 'PO', label: 'Purchase Order (PO)', icon: '📑' },
  { key: 'CANVASS', label: 'Canvass of Price', icon: '📝' },
  { key: 'PR-A&m', label: 'Purchase Request (PR)', icon: '📋' },
  { key: 'AOQ', label: 'Abstract of Quotation (AOQ)', icon: '⚖️' },
  { key: 'IAR', label: 'Inspection & Acceptance (IAR)', icon: '🔍' },
  { key: 'RIS', label: 'Requisition & Issue (RIS)', icon: '📦' },
  { key: 'ALL', label: 'All Appendices (Merged)', icon: '📚' }
]

const currentSheetLabel = computed(() => {
  const found = previewSheetsList.find(s => s.key === previewSheet.value)
  return found ? found.label : 'Form'
})

const loadPdfForCurrentSheet = async () => {
  if (!previewVoucherId.value) return
  const cacheKey = `${previewVoucherId.value}_${previewSheet.value}`
  
  if (pdfCache.value.has(cacheKey)) {
    if (pdfUrl.value && !pdfUrl.value.startsWith('blob:')) {
      // Keep
    }
    pdfUrl.value = pdfCache.value.get(cacheKey)
    pdfLoading.value = false
    return
  }

  pdfLoading.value = true
  pdfError.value = null

  try {
    const targetSheet = previewSheet.value === 'ALL' ? '' : previewSheet.value
    const url = await store.getPdfBlobUrl(previewVoucherId.value, targetSheet)
    pdfCache.value.set(cacheKey, url)
    pdfUrl.value = url
  } catch (err) {
    let msg = 'PDF generation is currently compiling or Microsoft Excel COM service is processing. You can also download the filled Excel document.'
    if (err.response?.data instanceof Blob) {
      try {
        const text = await err.response.data.text()
        const parsed = JSON.parse(text)
        if (parsed.detail) msg = parsed.detail
        else if (parsed.error) msg = parsed.error
      } catch (_) {}
    } else if (err.response?.data?.detail) {
      msg = err.response.data.detail
    } else if (err.response?.data?.error) {
      msg = err.response.data.error
    }
    pdfError.value = msg
  } finally {
    pdfLoading.value = false
  }
}

const changePreviewSheet = (sheetKey) => {
  if (previewSheet.value === sheetKey) return
  previewSheet.value = sheetKey
  loadPdfForCurrentSheet()
}

const openPdfPreview = async (id, transCode) => {
  previewVoucherId.value = id
  previewTransCode.value = transCode
  pdfCache.value.clear()
  previewSheet.value = 'DV'
  showPdfModal.value = true
  await loadPdfForCurrentSheet()
}

const downloadCurrentPdf = () => {
  const targetSheet = previewSheet.value === 'ALL' ? '' : previewSheet.value
  store.downloadPdf(previewVoucherId.value, previewTransCode.value, targetSheet)
}

const closePdfPreview = () => {
  pdfCache.value.forEach((url) => {
    try { window.URL.revokeObjectURL(url) } catch (e) {}
  })
  pdfCache.value.clear()
  pdfUrl.value = null
  showPdfModal.value = false
}

const showModal = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const currentTab = ref('GENERAL')

// Form Validation States
const validationErrors = ref([])
const invalidFieldKeys = ref(new Set())
const libValidationErrors = ref([])
const invalidLibFieldKeys = ref(new Set())

const isFieldInvalid = (key) => invalidFieldKeys.value.has(key)
const isLibFieldInvalid = (key) => invalidLibFieldKeys.value.has(key)
const hasTabErrors = (tabKey) => validationErrors.value.some(err => {
  if (err.tab === tabKey) return true
  if (err.tab === 'ITEMS' && (tabKey === 'PR' || tabKey === 'PO' || tabKey === 'RIS')) return true
  return false
})

const clearFieldError = (key) => {
  if (invalidFieldKeys.value.has(key)) {
    invalidFieldKeys.value.delete(key)
    validationErrors.value = validationErrors.value.filter(err => err.key !== key)
  }
}

const clearLibFieldError = (key) => {
  if (invalidLibFieldKeys.value.has(key)) {
    invalidLibFieldKeys.value.delete(key)
    libValidationErrors.value = libValidationErrors.value.filter(err => err.key !== key)
  }
}

// Library Management State
const selectedLibCategory = ref('TRANSACTION_TYPE')
const libSearchQuery = ref('')
const showLibModal = ref(false)
const isEditingLib = ref(false)
const libForm = ref({
  id: null,
  category: 'TRANSACTION_TYPE',
  code: '',
  name: '',
  description: '',
  address: '',
  tin: '',
  designation: '',
  is_active: true,
  sort_order: 0
})

const libraryCategories = [
  { key: 'TRANSACTION_TYPE', label: 'Transaction Types', icon: '🏷️' },
  { key: 'SUPPLIER', label: 'Suppliers / Payees', icon: '🏢' },
  { key: 'REQUESTED_BY', label: 'Requested By', icon: '✍️' },
  { key: 'APPROVED_BY', label: 'Approved By', icon: '👔' },
  { key: 'ISSUED_BY', label: 'Issued By', icon: '📦' },
  { key: 'RECEIVED_BY', label: 'Received By', icon: '🤝' },
  { key: 'MODE_OF_PROCUREMENT', label: 'Mode of Procurement', icon: '🛒' },
  { key: 'DELIVERY_TERM', label: 'Delivery Terms', icon: '🚚' },
  { key: 'PAYMENT_TERM', label: 'Payment Terms', icon: '💳' },
]

// Canvass Bidders 2 & 3
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
  await Promise.all([
    store.fetchTransactions(),
    store.fetchLibraries()
  ])
})

const getLibraryOptions = (category) => {
  return store.librariesByCategory(category)
}

const getLibraryCount = (category) => {
  return (store.libraries || []).filter(l => l.category === category).length
}

const currentLibCategoryLabel = computed(() => {
  const c = libraryCategories.find(c => c.key === selectedLibCategory.value)
  return c ? c.label : 'Library'
})

const filteredLibraries = computed(() => {
  return (store.libraries || []).filter(item => {
    const matchesCat = item.category === selectedLibCategory.value
    const query = libSearchQuery.value.toLowerCase().trim()
    const matchesQuery = !query ||
      item.name.toLowerCase().includes(query) ||
      (item.code && item.code.toLowerCase().includes(query)) ||
      (item.address && item.address.toLowerCase().includes(query)) ||
      (item.designation && item.designation.toLowerCase().includes(query))
    return matchesCat && matchesQuery
  })
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

    // Date filtering
    let matchesDate = true
    if (dateFrom.value || dateTo.value) {
      let rawDate = item[dateFilterField.value]
      if (rawDate) {
        // Date may be ISO string like '2026-10-19T03:30:00' or date format '2026-10-19'
        const dateStr = String(rawDate).slice(0, 10)
        if (dateFrom.value && dateStr < dateFrom.value) {
          matchesDate = false
        }
        if (dateTo.value && dateStr > dateTo.value) {
          matchesDate = false
        }
      } else {
        // If the item doesn't have the chosen date field populated, exclude when filtering
        matchesDate = false
      }
    }

    return matchesType && matchesStatus && matchesSearch && matchesDate
  })
})

// Summary Reporting Computeds
const summaryTotalSpend = computed(() => {
  return filteredTransactions.value.reduce((sum, t) => sum + Number(t.total_amount || 0), 0)
})

const transactionTypeMeta = [
  { type: 'SUPPLIES', label: 'Purchase of Supplies' },
  { type: 'REPAIR', label: 'Repair & Maintenance' },
  { type: 'CATERING', label: 'Catering Services' },
  { type: 'PETTY_CASH', label: 'Petty Cash Replenishment' },
  { type: 'TRAVEL', label: 'Travel Expenses' },
  { type: 'UTILITIES', label: 'Electricity & Internet' },
  { type: 'LOAD', label: 'Communication / Load' },
]

const reportByTypeData = computed(() => {
  const total = summaryTotalSpend.value || 1
  return transactionTypeMeta.map(meta => {
    const list = filteredTransactions.value.filter(t => t.transaction_type === meta.type)
    const totalAmount = list.reduce((sum, t) => sum + Number(t.total_amount || 0), 0)
    return {
      type: meta.type,
      label: meta.label,
      count: list.length,
      totalAmount,
      percent: summaryTotalSpend.value > 0 ? (totalAmount / total) * 100 : 0
    }
  }).sort((a, b) => b.totalAmount - a.totalAmount)
})

const reportByPayeeData = computed(() => {
  const map = new Map()
  const total = summaryTotalSpend.value || 1

  filteredTransactions.value.forEach(t => {
    const key = (t.payee_supplier_name || 'UNSPECIFIED PAYEE').trim()
    const amt = Number(t.total_amount || 0)
    if (!map.has(key)) {
      map.set(key, {
        name: key,
        address: t.payee_address || '',
        count: 0,
        totalAmount: 0
      })
    }
    const entry = map.get(key)
    entry.count += 1
    entry.totalAmount += amt
    if (!entry.address && t.payee_address) {
      entry.address = t.payee_address
    }
  })

  return Array.from(map.values())
    .map(p => ({
      ...p,
      percent: summaryTotalSpend.value > 0 ? (p.totalAmount / total) * 100 : 0
    }))
    .sort((a, b) => b.totalAmount - a.totalAmount)
})

const reportByItemData = computed(() => {
  const map = new Map()

  filteredTransactions.value.forEach(t => {
    (t.items || []).forEach(it => {
      const desc = (it.item_description || 'General Item').trim()
      const qty = Number(it.quantity || 0)
      const cost = Number(it.unit_cost_1 || 0)
      const itemTotal = qty * cost

      if (!map.has(desc)) {
        map.set(desc, {
          description: desc,
          unit: it.unit || 'unit',
          totalQty: 0,
          totalCost: 0,
          unitCosts: []
        })
      }
      const entry = map.get(desc)
      entry.totalQty += qty
      entry.totalCost += itemTotal
      if (cost > 0) entry.unitCosts.push(cost)
      if (it.unit && entry.unit === 'unit') entry.unit = it.unit
    })
  })

  const itemsArr = Array.from(map.values())
  const totalAllItemsCost = itemsArr.reduce((sum, i) => sum + i.totalCost, 0) || 1

  return itemsArr.map(i => {
    const avg = i.unitCosts.length > 0
      ? i.unitCosts.reduce((a, b) => a + b, 0) / i.unitCosts.length
      : (i.totalQty > 0 ? i.totalCost / i.totalQty : 0)
    return {
      description: i.description,
      unit: i.unit,
      totalQty: i.totalQty,
      avgUnitCost: avg,
      totalCost: i.totalCost,
      percent: totalAllItemsCost > 0 ? (i.totalCost / totalAllItemsCost) * 100 : 0
    }
  }).sort((a, b) => b.totalCost - a.totalCost)
})

const reportItemsTotalQty = computed(() => {
  return reportByItemData.value.reduce((sum, i) => sum + i.totalQty, 0)
})

const reportItemsTotalCost = computed(() => {
  return reportByItemData.value.reduce((sum, i) => sum + i.totalCost, 0)
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

const onSelectSupplier = (supplierName) => {
  if (!supplierName) return
  form.value.payee_supplier_name = supplierName
  const found = (store.libraries || []).find(l => l.category === 'SUPPLIER' && l.name === supplierName)
  if (found) {
    form.value.payee_address = found.address || form.value.payee_address
    form.value.payee_tin = found.tin || form.value.payee_tin
  }
}

const recalcItemTotal = (item) => {
  item.total_cost = (Number(item.quantity || 0) * Number(item.unit_cost_1 || 0))
}

const addItemRow = () => {
  if (!form.value.items) form.value.items = []
  const nextNum = form.value.items.length + 1
  form.value.items.push({
    item_number: nextNum,
    item_code: String(nextNum),
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

const openEditModal = async (id, targetTab = 'GENERAL') => {
  try {
    const data = await store.fetchVoucher(id)
    isEditing.value = true
    currentTab.value = targetTab

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

const validateForm = () => {
  validationErrors.value = []
  invalidFieldKeys.value.clear()

  // Tab 1: General & Payee
  if (!form.value.transaction_code || !form.value.transaction_code.trim()) {
    invalidFieldKeys.value.add('transaction_code')
    validationErrors.value.push({
      key: 'transaction_code',
      tab: 'GENERAL',
      tabName: '1 (Transaction & Liquidation)',
      message: 'Transaction Code is required.'
    })
  }

  if (!form.value.transaction_type) {
    invalidFieldKeys.value.add('transaction_type')
    validationErrors.value.push({
      key: 'transaction_type',
      tab: 'GENERAL',
      tabName: '1 (Transaction & Liquidation)',
      message: 'Transaction Type must be selected.'
    })
  }

  if (!form.value.payee_supplier_name || !form.value.payee_supplier_name.trim()) {
    invalidFieldKeys.value.add('payee_supplier_name')
    validationErrors.value.push({
      key: 'payee_supplier_name',
      tab: 'GENERAL',
      tabName: '1 (Transaction & Liquidation)',
      message: 'Primary Payee / Supplier Name is required.'
    })
  }

  // Tab 2: Items
  if (!form.value.items || form.value.items.length === 0) {
    invalidFieldKeys.value.add('items_list')
    validationErrors.value.push({
      key: 'items_list',
      tab: 'ITEMS',
      tabName: '2 (Items & Canvass)',
      message: 'At least one item must be added.'
    })
  } else {
    form.value.items.forEach((item, index) => {
      if (!item.description || !item.description.trim()) {
        const key = `item_desc_${index}`
        invalidFieldKeys.value.add(key)
        validationErrors.value.push({
          key,
          tab: 'ITEMS',
          tabName: '2 (Items & Canvass)',
          message: `Item #${index + 1}: Description is required.`
        })
      }
      if (!item.quantity || Number(item.quantity) <= 0) {
        const key = `item_qty_${index}`
        invalidFieldKeys.value.add(key)
        validationErrors.value.push({
          key,
          tab: 'ITEMS',
          tabName: '2 (Items & Canvass)',
          message: `Item #${index + 1}: Quantity must be greater than 0.`
        })
      }
      if (item.unit_cost_1 === undefined || item.unit_cost_1 === null || Number(item.unit_cost_1) < 0) {
        const key = `item_cost_${index}`
        invalidFieldKeys.value.add(key)
        validationErrors.value.push({
          key,
          tab: 'ITEMS',
          tabName: '2 (Items & Canvass)',
          message: `Item #${index + 1}: Supplier 1 unit cost is required.`
        })
      }
    })
  }

  return validationErrors.value.length === 0
}

const saveVoucher = async () => {
  if (!validateForm()) {
    // Jump user directly to the first tab that has an error
    const firstErr = validationErrors.value[0]
    if (firstErr && firstErr.tab) {
      currentTab.value = firstErr.tab
    }
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
    validationErrors.value = []
    invalidFieldKeys.value.clear()
    showModal.value = false
  } catch (err) {
    const errData = err.response?.data
    if (errData && typeof errData === 'object') {
      const parseErrorValue = (val) => {
        if (typeof val === 'string') return val
        if (Array.isArray(val)) {
          return val.map(item => parseErrorValue(item)).join('; ')
        }
        if (typeof val === 'object' && val !== null) {
          return Object.entries(val)
            .map(([k, v]) => `${k.replace('_', ' ')}: ${parseErrorValue(v)}`)
            .join(', ')
        }
        return String(val)
      }

      Object.keys(errData).forEach(field => {
        invalidFieldKeys.value.add(field)
        const msgStr = parseErrorValue(errData[field])
        
        let tabKey = 'GENERAL'
        let tabLabel = '1 (Transaction & Liquidation)'

        if (field === 'items' || field.startsWith('item')) {
          tabKey = 'ITEMS'
          tabLabel = '2 (Items & Canvass)'
        } else if (field === 'canvass_suppliers') {
          tabKey = 'ITEMS'
          tabLabel = '2 (Items & Canvass)'
        } else if (field.startsWith('ris_')) {
          tabKey = 'RIS'
          tabLabel = '3 (RIS)'
        } else if (field.startsWith('pr_')) {
          tabKey = 'PR'
          tabLabel = '4 (PR)'
        } else if (field.startsWith('po_')) {
          tabKey = 'PO'
          tabLabel = '5 (PO)'
        } else if (field.startsWith('iar_')) {
          tabKey = 'IAR'
          tabLabel = '6 (IAR)'
        } else if (field.startsWith('dv_')) {
          tabKey = 'DV'
          tabLabel = '7 (DV)'
        }

        validationErrors.value.push({
          key: field,
          tab: tabKey,
          tabName: tabLabel,
          message: `${field.replace('_', ' ').toUpperCase()}: ${msgStr}`
        })
      })

      // Jump user to the first error tab
      if (validationErrors.value.length > 0) {
        currentTab.value = validationErrors.value[0].tab
      }
    } else {
      alert('Error saving voucher transaction: ' + (err.message || 'Please check required fields.'))
    }
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

// Quick Add Supplier from Transaction Form
const openAddSupplierQuickModal = () => {
  isEditingLib.value = false
  selectedLibCategory.value = 'SUPPLIER'
  libForm.value = {
    id: null,
    category: 'SUPPLIER',
    code: '',
    name: '',
    description: '',
    address: '',
    tin: '',
    designation: '',
    is_active: true,
    sort_order: getLibraryCount('SUPPLIER') + 1
  }
  showLibModal.value = true
}

// Library actions
const openAddLibraryModal = () => {
  isEditingLib.value = false
  libForm.value = {
    id: null,
    category: selectedLibCategory.value,
    code: '',
    name: '',
    description: '',
    address: '',
    tin: '',
    designation: '',
    is_active: true,
    sort_order: getLibraryCount(selectedLibCategory.value) + 1
  }
  showLibModal.value = true
}

const openEditLibraryModal = (item) => {
  isEditingLib.value = true
  libForm.value = { ...item }
  showLibModal.value = true
}

const saveLibraryItem = async () => {
  libValidationErrors.value = []
  invalidLibFieldKeys.value.clear()

  if (!libForm.value.name || !libForm.value.name.trim()) {
    invalidLibFieldKeys.value.add('name')
    libValidationErrors.value.push({
      key: 'name',
      message: libForm.value.category === 'SUPPLIER'
        ? 'Supplier / Payee Name is required and cannot be blank.'
        : 'Name / Title is required and cannot be blank.'
    })
    return
  }
  try {
    let savedItem
    if (isEditingLib.value) {
      savedItem = await store.updateLibraryItem(libForm.value.id, libForm.value)
    } else {
      savedItem = await store.createLibraryItem(libForm.value)
      // If we are currently editing or creating a voucher and adding a supplier, auto-select it!
      if (savedItem.category === 'SUPPLIER' && showModal.value) {
        form.value.payee_supplier_name = savedItem.name
        form.value.payee_address = savedItem.address || form.value.payee_address
        form.value.payee_tin = savedItem.tin || form.value.payee_tin
      }
    }
    libValidationErrors.value = []
    invalidLibFieldKeys.value.clear()
    showLibModal.value = false
  } catch (err) {
    const errData = err.response?.data
    if (errData && typeof errData === 'object') {
      Object.keys(errData).forEach(field => {
        invalidLibFieldKeys.value.add(field)
        const msgs = Array.isArray(errData[field]) ? errData[field].join(' ') : String(errData[field])
        libValidationErrors.value.push({
          key: field,
          message: `${field.toUpperCase()}: ${msgs}`
        })
      })
    } else {
      const errorMsg = errData ? String(errData) : (err.message || 'Failed to save library record.')
      libValidationErrors.value.push({
        key: 'general',
        message: errorMsg
      })
    }
  }
}

const deleteLibraryItem = async (item) => {
  if (confirm(`Delete "${item.name}" from ${currentLibCategoryLabel.value}?`)) {
    try {
      await store.deleteLibraryItem(item.id)
    } catch (err) {
      alert('Failed to delete library record.')
    }
  }
}

const triggerDatePicker = (event) => {
  const container = event.currentTarget.closest('.date-picker-control')
  if (container) {
    const input = container.querySelector('input[type="date"]')
    if (input) {
      if (typeof input.showPicker === 'function') {
        input.showPicker()
      } else {
        input.focus()
      }
    }
  }
}
</script>

<style scoped>
/* Main Container — expands to full screen width */
.voucher-container {
  width: 100%;
  max-width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Header */
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-radius: var(--radius-md);
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left h2 {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 0.88rem;
  margin-top: 0.2rem;
}

.header-right {
  display: flex;
  gap: 0.65rem;
  align-items: center;
}

.btn-nav {
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 0.6rem 1rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 0.88rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  transition: all 0.2s ease;
}

.btn-nav:hover {
  background: rgba(29, 78, 216, 0.08);
  color: var(--accent-gold);
}

.btn-nav.active {
  background: var(--accent-gold);
  color: #ffffff;
  border-color: var(--accent-gold);
  box-shadow: 0 4px 14px rgba(29, 78, 216, 0.35);
}

.btn-primary {
  background: linear-gradient(135deg, #1d4ed8, #2563eb);
  color: #ffffff;
  border: 1px solid #1d4ed8;
  padding: 0.6rem 1.2rem;
  border-radius: var(--radius-sm);
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  transition: all 0.2s ease;
  box-shadow: 0 4px 14px rgba(29, 78, 216, 0.25);
}

.btn-primary:hover {
  background: linear-gradient(135deg, #1e40af, #1d4ed8);
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(29, 78, 216, 0.35);
}

.btn-secondary {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 0.6rem 1.1rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--bg-surface-elevated);
  border-color: var(--accent-gold);
  color: var(--accent-gold);
}

/* Flowchart Stage Summary Pills */
.flowchart-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.75rem;
  padding: 0.85rem 1rem;
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
}

.flow-step {
  padding: 0.65rem 0.5rem;
  border-radius: var(--radius-sm);
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.flow-step:hover {
  border-color: var(--accent-gold);
  background: rgba(29, 78, 216, 0.05);
  transform: translateY(-2px);
}

.flow-step.active {
  border-color: var(--accent-gold);
  background: rgba(29, 78, 216, 0.1);
  box-shadow: 0 4px 12px rgba(29, 78, 216, 0.15);
}

.flow-num {
  font-size: 0.75rem;
  font-weight: 800;
  color: var(--accent-gold);
}

.flow-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-top: 0.2rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.flow-count {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--text-primary);
  margin-top: 0.2rem;
}

/* Filter Bar */
.filter-bar {
  display: flex;
  flex-direction: column;
  padding: 1rem 1.25rem;
  border-radius: var(--radius-md);
  gap: 0.85rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
}

.filter-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  width: 100%;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  max-width: 480px;
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  padding: 0.45rem 0.85rem;
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.search-box:focus-within {
  border-color: var(--accent-gold);
  box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.12);
}

.search-input {
  width: 100%;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 0.88rem;
  outline: none;
}

.filter-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.select-filter {
  width: auto;
  min-width: 180px;
  padding: 0.45rem 0.75rem;
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  outline: none;
}

.select-filter:focus {
  border-color: var(--accent-gold);
}

.filter-info {
  font-size: 0.82rem;
  color: var(--text-muted);
}

/* Date Filter Controls */
.filter-date-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.85rem;
  padding-top: 0.75rem;
  border-top: 1px dashed var(--border-color);
  width: 100%;
}

.date-filter-group {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.date-filter-label {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text-secondary);
}

.select-filter-sm {
  font-size: 0.82rem;
  padding: 0.35rem 0.6rem;
  border-radius: var(--radius-sm);
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  outline: none;
}

.select-filter-sm:focus {
  border-color: var(--accent-gold);
}

.date-input-wrap {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.date-input-sm {
  font-size: 0.82rem;
  padding: 0.35rem 0.55rem;
  border-radius: var(--radius-sm);
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  outline: none;
}

.date-input-sm:focus {
  border-color: var(--accent-gold);
}

.btn-clear-date {
  background: rgba(225, 29, 72, 0.1);
  border: 1px solid rgba(225, 29, 72, 0.25);
  color: var(--accent-rose);
  padding: 0.32rem 0.6rem;
  border-radius: var(--radius-sm);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-clear-date:hover {
  background: var(--accent-rose);
  color: #ffffff;
}

.date-presets {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.preset-btn {
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 0.3rem 0.65rem;
  border-radius: var(--radius-sm);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.preset-btn:hover {
  border-color: var(--accent-gold);
  color: var(--accent-gold);
}

.preset-btn.active {
  background: var(--accent-gold);
  border-color: var(--accent-gold);
  color: #ffffff;
}

/* Table Wrapper */
.content-table-wrapper {
  border-radius: var(--radius-md);
  overflow: hidden;
  padding: 0.5rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
}

.table-responsive {
  width: 100%;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 0.85rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.data-table th {
  background: #f1f5f9;
  color: #1e3a8a;
  font-weight: 700;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.table-row:hover {
  background: rgba(29, 78, 216, 0.03);
}

.code-highlight {
  color: var(--accent-gold);
  font-family: monospace;
  font-size: 0.92rem;
}

.badge {
  display: inline-block;
  padding: 0.22rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.type-badge {
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
  font-weight: 700;
}

.status-badge {
  background: #ecfdf5;
  color: #065f46;
  border: 1px solid #a7f3d0;
  font-weight: 700;
}

.status-badge.draft {
  background: #f1f5f9;
  color: #334155;
  border-color: #cbd5e1;
  font-weight: 700;
}

.active-badge {
  background: #ecfdf5;
  color: #065f46;
  border: 1px solid #a7f3d0;
  font-weight: 700;
}

.inactive-badge {
  background: #fff1f2;
  color: #be123c;
  border: 1px solid #fecdd3;
  font-weight: 700;
}

.amount-cell {
  font-family: monospace;
  font-size: 0.95rem;
  white-space: nowrap;
  font-weight: 700;
  color: #0f172a;
}

.net-due {
  color: #059669;
  font-weight: 800;
}

.sub-info {
  font-size: 0.82rem;
  color: #475569;
}

.badge-count {
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

/* Actions */
.actions-cell {
  white-space: nowrap;
}

.btn-action {
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  padding: 0.35rem 0.55rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  margin-left: 0.35rem;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.sheet-shortcut {
  font-size: 0.76rem;
  font-weight: 700;
  padding: 0.28rem 0.48rem;
  border-radius: var(--radius-sm);
}

.po-btn {
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #1d4ed8;
}

.po-btn:hover {
  background: #dbeafe;
}

.ris-btn {
  background: #f0fdf4;
  border-color: #bbf7d0;
  color: #15803d;
}

.ris-btn:hover {
  background: #dcfce7;
}

.pr-btn {
  background: #fefce8;
  border-color: #fef08a;
  color: #a16207;
}

.pr-btn:hover {
  background: #fef9c3;
}

.aoq-btn {
  background: #faf5ff;
  border-color: #e9d5ff;
  color: #7e22ce;
}

.aoq-btn:hover {
  background: #f3e8ff;
}

.iar-btn {
  background: #fff7ed;
  border-color: #fed7aa;
  color: #c2410c;
}

.iar-btn:hover {
  background: #ffedd5;
}

.btn-action:hover {
  background: rgba(29, 78, 216, 0.1);
  border-color: var(--accent-gold);
  transform: translateY(-1px);
}

.btn-action.export:hover {
  background: rgba(16, 185, 129, 0.15);
  border-color: #10b981;
}

.btn-action.delete:hover {
  background: rgba(225, 29, 72, 0.15);
  border-color: var(--accent-rose);
}

/* Tabs Container (PDS Library style) */
.tabs-container {
  display: flex;
  overflow-x: auto;
  gap: 0.5rem;
  padding: 0.6rem;
  border-radius: var(--radius-md);
  scrollbar-width: thin;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.9rem;
  background: transparent;
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  background: var(--bg-surface-elevated);
  color: var(--text-primary);
}

.tab-btn.active {
  background: var(--accent-gold);
  color: #ffffff;
  font-weight: 700;
}

.tab-badge {
  background: rgba(0, 0, 0, 0.25);
  padding: 0.15rem 0.45rem;
  border-radius: 12px;
  font-size: 0.72rem;
}

.tab-btn.active .tab-badge {
  background: #172554;
  color: #ffffff;
}

/* Fullscreen / Large Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: var(--glass-backdrop);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-fullscreen {
  width: 98vw;
  max-width: 1400px;
  height: 94vh;
  display: flex;
  flex-direction: column;
  border-radius: var(--radius-lg);
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.25);
  overflow: hidden;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
}

.modal-medium {
  width: 550px;
  max-width: 95vw;
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.2);
}

.modal-header {
  padding: 1.25rem 1.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-surface);
}

.modal-subtitle {
  font-size: 0.82rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.btn-close {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.35rem;
  cursor: pointer;
  transition: color 0.15s ease;
}

.btn-close:hover {
  color: var(--accent-rose);
}

/* Wizard Navigation in Modal */
.wizard-nav {
  display: flex;
  overflow-x: auto;
  padding: 0.5rem 1.25rem;
  gap: 0.5rem;
  border-radius: 0;
  border-left: none;
  border-right: none;
  scrollbar-width: thin;
  background: var(--bg-surface-elevated);
  border-bottom: 1px solid var(--border-color);
}

.nav-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 0.95rem;
  background: transparent;
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.nav-tab:hover {
  background: var(--bg-surface);
  color: var(--text-primary);
}

.nav-tab.active {
  background: var(--accent-gold);
  color: #ffffff;
  font-weight: 700;
}

.tab-index {
  background: rgba(0, 0, 0, 0.25);
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.nav-tab.active .tab-index {
  background: #172554;
  color: #ffffff;
}

/* Modal Body & Sections */
.modal-body {
  padding: 1.75rem;
  overflow-y: auto;
  flex: 1;
}

.section-title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.85rem;
}

.section-sub {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 0.2rem;
}

.sheet-indicator {
  font-size: 0.75rem;
  font-weight: 700;
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  color: var(--accent-gold);
  padding: 0.25rem 0.65rem;
  border-radius: 12px;
}

.sub-heading {
  font-size: 0.92rem;
  color: var(--accent-gold);
  margin: 1.25rem 0 0.75rem;
  border-bottom: 1px dashed rgba(254, 203, 144, 0.25);
  padding-bottom: 0.35rem;
}

/* Grids & Fields */
.form-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.form-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.form-grid-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 1rem; }

@media (max-width: 900px) {
  .form-grid-2, .form-grid-3, .form-grid-4 {
    grid-template-columns: 1fr;
  }
}

.field label {
  display: block;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 0.35rem;
}

.canvass-box {
  padding: 1rem;
  border-radius: var(--radius-sm);
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
}

.table-input {
  width: 100%;
  padding: 0.4rem 0.5rem;
  font-size: 0.85rem;
}

.table-header-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1.5rem;
  margin-bottom: 0.6rem;
  padding-top: 0.85rem;
  border-top: 1px dashed var(--border-color);
}

/* DV Calculation Box */
.dv-computation-card {
  background: rgba(24, 17, 11, 0.85);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  max-width: 650px;
  margin: 1.5rem auto 0 auto;
  border: 1px solid var(--border-color);
}

.dv-calc-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.65rem 0;
  border-bottom: 1px solid rgba(254, 203, 144, 0.08);
}

.dv-calc-row.due-row {
  border-top: 2px solid var(--accent-gold);
  border-bottom: none;
  margin-top: 0.75rem;
  padding-top: 1rem;
}

.calc-label {
  color: var(--text-secondary);
  font-size: 0.92rem;
}

.calc-val {
  font-size: 1.1rem;
}

.due-val {
  color: #34d399;
  font-size: 1.4rem;
  font-weight: 800;
}

.text-danger {
  color: #f87171;
}

.text-accent {
  color: var(--accent-gold);
}

.mini-select {
  width: auto;
  padding: 0.2rem 0.5rem;
  font-size: 0.8rem;
  margin-left: 0.5rem;
}

/* Modal Footer */
.modal-footer {
  padding: 1rem 1.75rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.footer-summary {
  font-size: 0.88rem;
  color: var(--text-secondary);
}

.footer-btns {
  display: flex;
  gap: 0.75rem;
}

/* Helpers & States */
.code-badge {
  padding: 0.15rem 0.4rem;
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 0.75rem;
}

.no-records {
  text-align: center;
  color: var(--text-muted);
  padding: 2.5rem 1rem;
  font-size: 0.9rem;
}

.empty-state, .loading-state {
  text-align: center;
  padding: 3rem 1.5rem;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(254, 203, 144, 0.2);
  border-top-color: var(--accent-gold);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.modal-pdf-preview {
  width: 95vw;
  max-width: 1300px;
  height: 92vh;
  display: flex;
  flex-direction: column;
}

.pdf-sheet-bar {
  display: flex;
  overflow-x: auto;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  border-radius: 0;
  border-left: none;
  border-right: none;
  scrollbar-width: thin;
  background: rgba(29, 21, 14, 0.9);
}

.pdf-sheet-btn {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.75rem;
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.pdf-sheet-btn:hover {
  background: var(--bg-surface-elevated);
  color: var(--text-primary);
  border-color: rgba(254, 203, 144, 0.2);
}

.pdf-sheet-btn.active {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  font-weight: 700;
  border-color: var(--accent-gold);
  box-shadow: 0 2px 8px rgba(254, 203, 144, 0.3);
}

.pdf-body {
  padding: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.pdf-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: #ffffff;
  border-bottom-left-radius: var(--radius-md);
  border-bottom-right-radius: var(--radius-md);
}

.btn-action.preview-pdf {
  color: var(--accent-gold);
  border-color: rgba(254, 203, 144, 0.4);
}

.btn-action.preview-pdf:hover {
  background: rgba(254, 203, 144, 0.25);
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-link-action {
  background: transparent;
  border: none;
  color: var(--accent-gold);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  transition: opacity 0.2s;
}

.btn-link-action:hover {
  text-decoration: underline;
  opacity: 0.85;
}

.mt-1 { margin-top: 0.25rem; }
.mt-3 { margin-top: 0.75rem; }
.mb-1 { margin-bottom: 0.25rem; }
.mb-3 { margin-bottom: 0.75rem; }
.mb-4 { margin-bottom: 1rem; }
.mr-2 { margin-right: 0.5rem; }
.font-mono { font-family: monospace; }
.font-bold { font-weight: 700; }
.font-semibold { font-weight: 600; }
.font-medium { font-weight: 500; }
.text-muted { color: var(--text-muted); }
.text-right { text-align: right; }

/* ========================================================================= */
/* VALIDATION & ERROR HIGHLIGHTING STYLES */
/* ========================================================================= */
.validation-banner {
  background: #fff1f2;
  border: 1.5px solid #fecdd3;
  border-radius: var(--radius-md);
  padding: 0.9rem 1.25rem;
  margin: 0.75rem 1.5rem 0.25rem 1.5rem;
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  animation: slideDown 0.25s ease-out;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}

.banner-icon {
  font-size: 1.35rem;
  line-height: 1;
  padding-top: 0.1rem;
}

.banner-content {
  flex: 1;
  font-size: 0.88rem;
  color: #9f1239;
}

.banner-content strong {
  color: #881337;
  font-weight: 700;
  display: block;
  margin-bottom: 0.35rem;
}

.banner-content ul {
  margin: 0;
  padding-left: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.error-link {
  color: #be123c;
  cursor: pointer;
  text-decoration: underline;
  font-weight: 600;
  transition: color 0.15s ease;
}

.error-link:hover {
  color: #4c0519;
}

.tab-jump-hint {
  font-size: 0.78rem;
  color: #64748b;
  font-weight: 600;
  margin-left: 0.35rem;
}

.btn-clear-errors {
  background: transparent;
  border: none;
  color: #be123c;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0.2rem 0.5rem;
  line-height: 1;
  border-radius: 4px;
}

.btn-clear-errors:hover {
  background: #ffe4e6;
  color: #881337;
}

/* Tab Error Indicator */
.nav-tab.has-tab-error {
  border-bottom: 2px solid #e11d48 !important;
  color: #be123c;
  font-weight: 700;
}

.tab-error-dot {
  background: #e11d48;
  color: #ffffff;
  font-size: 0.72rem;
  font-weight: 800;
  width: 17px;
  height: 17px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-left: 0.35rem;
  box-shadow: 0 0 8px rgba(225, 29, 72, 0.4);
  animation: pulse 1.6s infinite ease-in-out;
}

@keyframes pulse {
  0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(225, 29, 72, 0.5); }
  70% { transform: scale(1.1); box-shadow: 0 0 0 6px rgba(225, 29, 72, 0); }
  100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(225, 29, 72, 0); }
}

/* Invalid Input Highlighting */
.input-invalid,
input.input-invalid,
select.input-invalid,
textarea.input-invalid {
  border-color: #e11d48 !important;
  box-shadow: 0 0 0 2.5px rgba(225, 29, 72, 0.2) !important;
  background-color: #fff1f2 !important;
  color: #0f172a !important;
}

.input-invalid:focus,
input.input-invalid:focus,
select.input-invalid:focus,
textarea.input-invalid:focus {
  border-color: #be123c !important;
  box-shadow: 0 0 0 3px rgba(225, 29, 72, 0.3) !important;
  outline: none;
}

.field-has-error label {
  color: #be123c !important;
  font-weight: 700;
}

.req-star {
  font-size: 0.75rem;
  margin-left: 0.25rem;
}

.error-inline-msg {
  display: block;
  font-size: 0.75rem;
  color: #be123c;
  margin-top: 0.25rem;
  font-weight: 600;
}

/* ========================================================================= */
/* ENHANCED CALENDAR CONTROL STYLING */
/* ========================================================================= */
.date-picker-control {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.date-picker-control input[type="date"] {
  width: 100%;
  padding-right: 2.2rem;
  cursor: pointer;
}

.date-picker-control .calendar-icon-btn {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  pointer-events: none;
  color: var(--accent-gold);
  opacity: 0.9;
  display: flex;
  align-items: center;
  justify-content: center;
}

.date-picker-control:hover input[type="date"] {
  border-color: var(--accent-gold);
}

.date-picker-control:hover .calendar-icon-btn {
  transform: translateY(-50%) scale(1.1);
  opacity: 1;
}

/* ========================================================================= */
/* SUMMARY REPORTING MODAL & PRINT STYLES */
/* ========================================================================= */
.report-modal {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
}

.report-header-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.report-icon {
  font-size: 1.8rem;
  background: rgba(29, 78, 216, 0.1);
  padding: 0.5rem;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.report-header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.report-tabs-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.75rem;
  background: var(--bg-surface-elevated);
  border-bottom: 1px solid var(--border-color);
  overflow-x: auto;
}

.report-tab-btn {
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.88rem;
  padding: 0.55rem 1.1rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.report-tab-btn:hover {
  background: var(--bg-surface);
  color: var(--accent-gold);
}

.report-tab-btn.active {
  background: var(--accent-gold);
  color: #ffffff;
  border-color: var(--accent-gold);
  box-shadow: 0 4px 12px rgba(29, 78, 216, 0.2);
}

.report-body {
  padding: 1.5rem 2rem;
  overflow-y: auto;
  flex: 1;
  background: #f8fafc;
}

.report-scope-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  padding: 0.85rem 1.25rem;
  border-radius: var(--radius-md);
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
}

.scope-item {
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.scope-lbl {
  color: var(--text-muted);
}

.text-royal {
  color: var(--accent-gold) !important;
}

.report-cards-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
}

.report-stat-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
  transition: transform 0.2s ease;
}

.report-stat-card:hover {
  transform: translateY(-2px);
  border-color: var(--accent-gold);
}

.stat-type-label {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-amount {
  font-size: 1.45rem;
  font-weight: 800;
  color: #1e3a8a;
  margin: 0.4rem 0;
  font-family: monospace;
}

.stat-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: 0.6rem;
}

.stat-progress-bar {
  width: 100%;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.stat-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #1d4ed8, #3b82f6);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.report-table-box {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(15, 23, 42, 0.04);
}

.report-box-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-surface-elevated);
}

.report-box-header h4 {
  font-size: 0.95rem;
  color: var(--text-primary);
  font-weight: 700;
}

.report-table {
  width: 100%;
  border-collapse: collapse;
}

.report-table th,
.report-table td {
  padding: 0.85rem 1.25rem;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.88rem;
}

.report-table th {
  background: #f1f5f9;
  color: #1e3a8a;
  font-weight: 700;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.report-table tbody tr:hover {
  background: rgba(29, 78, 216, 0.02);
}

.report-total-row {
  background: #f8fafc;
  font-weight: 800;
  border-top: 2px solid #cbd5e1;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e2e8f0;
  color: #475569;
  font-size: 0.75rem;
  font-weight: 700;
}

.rank-badge.top-rank {
  background: linear-gradient(135deg, #1d4ed8, #2563eb);
  color: #ffffff;
}

@media print {
  body * {
    visibility: hidden;
  }
  #printableReportArea, #printableReportArea * {
    visibility: visible;
  }
  #printableReportArea {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    padding: 0;
    background: #ffffff !important;
  }
}
</style>
