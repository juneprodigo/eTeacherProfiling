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
                    class="btn-action edit"
                    title="Edit and Review All Forms"
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
            <span>Items &amp; Canvass (1, 2, 3)</span>
            <span v-if="hasTabErrors('ITEMS')" class="tab-error-dot" title="Missing required fields">!</span>
          </button>
          <button
            class="nav-tab"
            :class="{ active: currentTab === 'RIS', 'has-tab-error': hasTabErrors('RIS') }"
            @click="currentTab = 'RIS'"
          >
            <span class="tab-index">3</span>
            <span>RIS (Appendix 63)</span>
            <span v-if="hasTabErrors('RIS')" class="tab-error-dot" title="Missing required fields">!</span>
          </button>
          <button
            class="nav-tab"
            :class="{ active: currentTab === 'PR', 'has-tab-error': hasTabErrors('PR') }"
            @click="currentTab = 'PR'"
          >
            <span class="tab-index">4</span>
            <span>PR (Appendix 60)</span>
            <span v-if="hasTabErrors('PR')" class="tab-error-dot" title="Missing required fields">!</span>
          </button>
          <button
            class="nav-tab"
            :class="{ active: currentTab === 'PO', 'has-tab-error': hasTabErrors('PO') }"
            @click="currentTab = 'PO'"
          >
            <span class="tab-index">5</span>
            <span>PO (Appendix 61)</span>
            <span v-if="hasTabErrors('PO')" class="tab-error-dot" title="Missing required fields">!</span>
          </button>
          <button
            class="nav-tab"
            :class="{ active: currentTab === 'IAR', 'has-tab-error': hasTabErrors('IAR') }"
            @click="currentTab = 'IAR'"
          >
            <span class="tab-index">6</span>
            <span>IAR (Appendix 62)</span>
            <span v-if="hasTabErrors('IAR')" class="tab-error-dot" title="Missing required fields">!</span>
          </button>
          <button
            class="nav-tab"
            :class="{ active: currentTab === 'DV', 'has-tab-error': hasTabErrors('DV') }"
            @click="currentTab = 'DV'"
          >
            <span class="tab-index">7</span>
            <span>Disbursement Voucher (DV)</span>
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
          </div>

          <!-- TAB 4: Purchase Request (PR - Appendix 60) -->
          <div v-show="currentTab === 'PR'" class="form-section">
            <div class="section-title-row">
              <div>
                <h3>Appendix 60: Purchase Request (PR)</h3>
                <p class="section-sub">Standard DepEd Purchase Request Appendix 60</p>
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
          </div>

          <!-- TAB 5: Purchase Order (PO - Appendix 61) -->
          <div v-show="currentTab === 'PO'" class="form-section">
            <div class="section-title-row">
              <div>
                <h3>Appendix 61: Purchase Order (PO)</h3>
                <p class="section-sub">Procurement Terms and Conditions</p>
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
          </div>

          <!-- TAB 6: Inspection & Acceptance Report (IAR - Appendix 62) -->
          <div v-show="currentTab === 'IAR'" class="form-section">
            <div class="section-title-row">
              <div>
                <h3>Appendix 62: Inspection &amp; Acceptance Report (IAR)</h3>
                <p class="section-sub">Inspection verification and Property Custodian acceptance</p>
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
    pdfError.value = 'PDF generation is currently compiling or Microsoft Excel COM service is processing. You can also download the filled Excel document.'
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
const hasTabErrors = (tabKey) => validationErrors.value.some(err => err.tab === tabKey)

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
  background: rgba(254, 203, 144, 0.15);
  color: var(--accent-gold);
}

.btn-nav.active {
  background: var(--accent-gold);
  color: var(--text-on-accent, #26150a);
  border-color: var(--accent-gold);
  box-shadow: 0 4px 14px rgba(254, 203, 144, 0.35);
}

.btn-primary {
  background: linear-gradient(135deg, #fecb90, #f8b668);
  color: #26150a;
  border: 1px solid #fecb90;
  padding: 0.6rem 1.2rem;
  border-radius: var(--radius-sm);
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  transition: all 0.2s ease;
  box-shadow: 0 4px 14px rgba(254, 203, 144, 0.3);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(254, 203, 144, 0.4);
}

.btn-secondary {
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 0.6rem 1.1rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
}

.btn-secondary:hover {
  background: rgba(254, 203, 144, 0.15);
  color: var(--text-primary);
}

/* Flowchart Stage Summary Pills */
.flowchart-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.75rem;
  padding: 0.85rem 1rem;
  border-radius: var(--radius-md);
}

.flow-step {
  padding: 0.65rem 0.5rem;
  border-radius: var(--radius-sm);
  background: rgba(24, 17, 11, 0.6);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.flow-step:hover {
  border-color: var(--accent-gold);
  background: rgba(254, 203, 144, 0.1);
  transform: translateY(-2px);
}

.flow-step.active {
  border-color: var(--accent-gold);
  background: rgba(254, 203, 144, 0.2);
  box-shadow: 0 4px 12px rgba(254, 203, 144, 0.25);
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
  justify-content: space-between;
  align-items: center;
  padding: 0.85rem 1.25rem;
  border-radius: var(--radius-md);
  flex-wrap: wrap;
  gap: 0.75rem;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  max-width: 480px;
  background: rgba(24, 17, 11, 0.75);
  border: 1px solid var(--border-color);
  padding: 0.45rem 0.85rem;
  border-radius: var(--radius-sm);
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
}

.filter-info {
  font-size: 0.82rem;
  color: var(--text-muted);
}

/* Table Wrapper */
.content-table-wrapper {
  border-radius: var(--radius-md);
  overflow: hidden;
  padding: 0.5rem;
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
  background: rgba(36, 26, 18, 0.9);
  color: var(--accent-gold);
  font-weight: 700;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.table-row:hover {
  background: rgba(254, 203, 144, 0.04);
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
  background: rgba(254, 203, 144, 0.18);
  color: var(--accent-gold);
  border: 1px solid rgba(254, 203, 144, 0.3);
}

.status-badge {
  background: rgba(16, 185, 129, 0.2);
  color: #6ee7b7;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-badge.draft {
  background: rgba(191, 161, 137, 0.2);
  color: var(--text-muted);
  border-color: rgba(191, 161, 137, 0.3);
}

.active-badge {
  background: rgba(16, 185, 129, 0.2);
  color: #6ee7b7;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.inactive-badge {
  background: rgba(244, 63, 94, 0.2);
  color: #fda4af;
  border: 1px solid rgba(244, 63, 94, 0.3);
}

.amount-cell {
  font-family: monospace;
  font-size: 0.95rem;
  white-space: nowrap;
}

.net-due {
  color: #34d399;
}

.sub-info {
  font-size: 0.82rem;
  color: var(--text-secondary);
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

.btn-action:hover {
  background: rgba(254, 203, 144, 0.2);
  border-color: var(--accent-gold);
  transform: translateY(-1px);
}

.btn-action.export:hover {
  background: rgba(16, 185, 129, 0.25);
  border-color: #10b981;
}

.btn-action.delete:hover {
  background: rgba(244, 63, 94, 0.25);
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
  color: var(--text-on-accent, #24120a);
  font-weight: 700;
}

.tab-badge {
  background: rgba(0, 0, 0, 0.25);
  padding: 0.15rem 0.45rem;
  border-radius: 12px;
  font-size: 0.72rem;
}

.tab-btn.active .tab-badge {
  background: #24120a;
  color: var(--accent-gold);
}

/* Fullscreen / Large Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
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
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.7);
  overflow: hidden;
}

.modal-medium {
  width: 550px;
  max-width: 95vw;
  border-radius: var(--radius-md);
}

.modal-header {
  padding: 1.25rem 1.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
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
  background: var(--bg-surface-elevated);
  color: var(--text-primary);
}

.nav-tab.active {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  font-weight: 700;
}

.tab-index {
  background: rgba(0, 0, 0, 0.25);
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.nav-tab.active .tab-index {
  background: var(--text-on-accent, #24120a);
  color: var(--accent-gold);
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
  background: rgba(244, 63, 94, 0.12);
  border: 1.5px solid rgba(244, 63, 94, 0.55);
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
  color: #fecdd3;
}

.banner-content strong {
  color: #fff1f2;
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
  color: #fda4af;
  cursor: pointer;
  text-decoration: underline;
  transition: color 0.15s ease;
}

.error-link:hover {
  color: #ffffff;
}

.tab-jump-hint {
  font-size: 0.78rem;
  color: #fca5a5;
  font-weight: 600;
  margin-left: 0.35rem;
}

.btn-clear-errors {
  background: transparent;
  border: none;
  color: #fda4af;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0.2rem 0.5rem;
  line-height: 1;
  border-radius: 4px;
}

.btn-clear-errors:hover {
  background: rgba(244, 63, 94, 0.25);
  color: #ffffff;
}

/* Tab Error Indicator */
.nav-tab.has-tab-error {
  border-bottom: 2px solid #f43f5e !important;
  color: #fda4af;
}

.tab-error-dot {
  background: #f43f5e;
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
  box-shadow: 0 0 8px rgba(244, 63, 94, 0.8);
  animation: pulse 1.6s infinite ease-in-out;
}

@keyframes pulse {
  0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(244, 63, 94, 0.7); }
  70% { transform: scale(1.1); box-shadow: 0 0 0 6px rgba(244, 63, 94, 0); }
  100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(244, 63, 94, 0); }
}

/* Invalid Input Highlighting */
.input-invalid,
input.input-invalid,
select.input-invalid,
textarea.input-invalid {
  border-color: #f43f5e !important;
  box-shadow: 0 0 0 2.5px rgba(244, 63, 94, 0.35) !important;
  background-color: rgba(244, 63, 94, 0.08) !important;
  color: #fff1f2 !important;
}

.input-invalid:focus,
input.input-invalid:focus,
select.input-invalid:focus,
textarea.input-invalid:focus {
  border-color: #fb7185 !important;
  box-shadow: 0 0 0 3.5px rgba(244, 63, 94, 0.5) !important;
  outline: none;
}

.field-has-error label {
  color: #fda4af !important;
}

.req-star {
  font-size: 0.75rem;
  margin-left: 0.25rem;
}

.error-inline-msg {
  display: block;
  font-size: 0.75rem;
  color: #fda4af;
  margin-top: 0.25rem;
  font-weight: 500;
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
</style>
