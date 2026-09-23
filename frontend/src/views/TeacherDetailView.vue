<template>
  <div v-if="loading" class="loading-state">
    <div class="spinner"></div>
    <p>Loading CS Form 212 Dossier...</p>
  </div>

  <div v-else-if="pds" class="pds-wizard-container">
    <!-- Top Header Profile Banner -->
    <div class="teacher-banner glass-panel">
      <div class="banner-avatar">
        {{ pds.user?.first_name?.charAt(0) || 'T' }}
      </div>
      <div class="banner-info">
        <h2>{{ pds.user?.full_name }}</h2>
        <p class="role-desc">
          <span>{{ pds.position || 'Faculty Member' }}</span> • 
          <span>{{ pds.department || 'Academic Department' }}</span> • 
          <span>Employee ID: {{ pds.employee_id || 'N/A' }}</span>
        </p>
      </div>
      <div class="banner-actions">
        <button @click="showPreviewModal = true" class="btn-preview-banner" title="Preview CS Form 212">
          👁️ Preview PDS
        </button>
        <button @click="downloadPDF" class="btn-export" title="Export PDF File">
          📄 Export PDF
        </button>
        <button @click="downloadExcel" class="btn-export-excel" :disabled="isDownloadingExcel" title="Download Official Excel Template (.xlsx)">
          <span v-if="isDownloadingExcel" class="spinner-sm"></span>
          <span v-else>📊 Download Excel</span>
        </button>
        <button @click="showUserProfileModal = true" class="btn-account-profile" title="Edit User Information (Name, Email, Profile Photo, Password)">
          ⚙️ Account Settings
        </button>
      </div>
    </div>

    <!-- Multi-section Wizard Tabs (All 8 CSC Sections + Questions + References + Declaration) -->
    <div class="wizard-nav glass-panel">
      <button
        v-for="(sec, idx) in sections"
        :key="idx"
        :class="['nav-tab', { active: currentSection === idx }]"
        @click="currentSection = idx"
      >
        <span class="tab-index">{{ sec.num }}</span>
        <span class="tab-name">{{ sec.title }}</span>
      </button>
    </div>

    <!-- Section Content Panels -->
    <div class="section-content glass-panel">

      <!-- ===================================================================== -->
      <!-- SECTION I: PERSONAL INFORMATION (Items 1-21) -->
      <!-- ===================================================================== -->
      <div v-if="currentSection === 0" class="form-section">
        <div class="section-title-row">
          <div>
            <h3>I. Personal Information (Items 1–21)</h3>
            <p class="section-sub">Official legal identity and demographic records as per Revised 2026 PDS</p>
          </div>
          <span class="sheet-indicator">Sheet C1</span>
        </div>

        <form @submit.prevent="savePersonal">
          <h4 class="sub-heading">Legal Name &amp; Extension</h4>
          <div class="form-grid-4">
            <div class="field">
              <label>1. Surname *</label>
              <input v-model="formPersonal.surname" required placeholder="Last name" />
            </div>
            <div class="field">
              <label>2. First Name *</label>
              <input v-model="formPersonal.first_name" required placeholder="First name" />
            </div>
            <div class="field">
              <label>Middle Name</label>
              <input v-model="formPersonal.middle_name" placeholder="Leave blank or N/A" />
            </div>
            <div class="field">
              <label>Name Extension</label>
              <input v-model="formPersonal.name_extension" placeholder="e.g. JR., SR., III" />
            </div>
          </div>

          <h4 class="sub-heading">Birth &amp; Demographics</h4>
          <div class="form-grid-4">
            <div class="field">
              <label>3. Date of Birth (dd/mm/yyyy)</label>
              <input v-model="formPersonal.date_of_birth" type="date" />
            </div>
            <div class="field">
              <label>4. Place of Birth</label>
              <input v-model="formPersonal.place_of_birth" placeholder="City/Municipality, Province" />
            </div>
            <div class="field">
              <label>5. Sex at Birth</label>
              <select v-model="formPersonal.sex_at_birth">
                <option value="">Select</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
              </select>
            </div>
            <div class="field">
              <label>6. Civil Status</label>
              <select v-model="formPersonal.civil_status">
                <option value="">Select</option>
                <option value="Single">Single</option>
                <option value="Married">Married</option>
                <option value="Widow/er">Widow/er</option>
                <option value="Separated">Separated</option>
                <option value="Solo Parent">Solo Parent</option>
                <option value="Others">Others</option>
              </select>
            </div>
          </div>

          <div v-if="formPersonal.civil_status === 'Others'" class="form-grid-1">
            <div class="field">
              <label>Specify Civil Status (Others)</label>
              <input v-model="formPersonal.civil_status_others" placeholder="Please specify status..." />
            </div>
          </div>

          <div class="form-grid-3">
            <div class="field">
              <label>7. Height (m)</label>
              <input v-model="formPersonal.height_m" type="number" step="0.01" placeholder="e.g. 1.65" />
            </div>
            <div class="field">
              <label>8. Weight (kg)</label>
              <input v-model="formPersonal.weight_kg" type="number" step="0.1" placeholder="e.g. 62.5" />
            </div>
            <div class="field">
              <label>9. Blood Type</label>
              <select v-model="formPersonal.blood_type">
                <option value="">Select</option>
                <option value="A+">A+</option>
                <option value="A-">A-</option>
                <option value="B+">B+</option>
                <option value="B-">B-</option>
                <option value="AB+">AB+</option>
                <option value="AB-">AB-</option>
                <option value="O+">O+</option>
                <option value="O-">O-</option>
              </select>
            </div>
          </div>

          <h4 class="sub-heading">16. Citizenship (Item 16)</h4>
          <div class="citizenship-box">
            <div class="checkbox-row">
              <label class="cb-label">
                <input type="checkbox" v-model="formPersonal.citizenship_filipino" />
                <span>Filipino</span>
              </label>
              <label class="cb-label">
                <input type="checkbox" v-model="formPersonal.dual_citizenship" />
                <span>Dual Citizenship</span>
              </label>
            </div>

            <div v-if="formPersonal.dual_citizenship" class="dual-options">
              <div class="checkbox-row">
                <label class="cb-label">
                  <input type="checkbox" v-model="formPersonal.dual_citizenship_by_birth" />
                  <span>by birth</span>
                </label>
                <label class="cb-label">
                  <input type="checkbox" v-model="formPersonal.dual_citizenship_by_naturalization" />
                  <span>by naturalization</span>
                </label>
              </div>
              <div class="field mt-2">
                <label>Pls. indicate foreign country:</label>
                <input v-model="formPersonal.dual_citizenship_country" placeholder="e.g. United States, Canada" />
              </div>
            </div>
          </div>

          <h4 class="sub-heading">Government Identification Numbers (Items 10–15)</h4>
          <div class="form-grid-3">
            <div class="field">
              <label>10. UMID ID NO.</label>
              <input v-model="formPersonal.umid_id_no" placeholder="N/A if none" />
            </div>
            <div class="field">
              <label>11. PAG-IBIG ID NO.</label>
              <input v-model="formPersonal.pag_ibig_id_no" placeholder="N/A if none" />
            </div>
            <div class="field">
              <label>12. PHILHEALTH NO.</label>
              <input v-model="formPersonal.philhealth_no" placeholder="N/A if none" />
            </div>
          </div>

          <div class="form-grid-3">
            <div class="field">
              <label>13. PhilSys Card (PCN)</label>
              <input v-model="formPersonal.philsys_pcn" placeholder="PhilSys Number" />
            </div>
            <div class="field">
              <label>14. TIN NO.</label>
              <input v-model="formPersonal.tin_no" placeholder="Tax Identification No." />
            </div>
            <div class="field">
              <label>15. Agency Employee No.</label>
              <input v-model="formPersonal.agency_employee_no" placeholder="Current Employee ID" />
            </div>
          </div>

          <h4 class="sub-heading">17. Residential Address</h4>
          <div class="form-grid-3">
            <div class="field">
              <label>House/Block/Lot No.</label>
              <input v-model="formPersonal.res_house_block_lot" />
            </div>
            <div class="field">
              <label>Street</label>
              <input v-model="formPersonal.res_street" />
            </div>
            <div class="field">
              <label>Subdivision/Village</label>
              <input v-model="formPersonal.res_subdivision_village" />
            </div>
          </div>
          <PhilippineAddressSelector
            v-model:province="formPersonal.res_province"
            v-model:cityMunicipality="formPersonal.res_city_municipality"
            v-model:barangay="formPersonal.res_barangay"
            v-model:zipCode="formPersonal.res_zip_code"
          />

          <div class="address-header-row">
            <h4 class="sub-heading">18. Permanent Address</h4>
            <button type="button" @click="copyResidentialToPermanent" class="btn-copy-address">
              ↳ Same as Residential Address
            </button>
          </div>
          <div class="form-grid-3">
            <div class="field">
              <label>House/Block/Lot No.</label>
              <input v-model="formPersonal.perm_house_block_lot" />
            </div>
            <div class="field">
              <label>Street</label>
              <input v-model="formPersonal.perm_street" />
            </div>
            <div class="field">
              <label>Subdivision/Village</label>
              <input v-model="formPersonal.perm_subdivision_village" />
            </div>
          </div>
          <PhilippineAddressSelector
            v-model:province="formPersonal.perm_province"
            v-model:cityMunicipality="formPersonal.perm_city_municipality"
            v-model:barangay="formPersonal.perm_barangay"
            v-model:zipCode="formPersonal.perm_zip_code"
          />

          <h4 class="sub-heading">Contact Information (Items 19–21)</h4>
          <div class="form-grid-3">
            <div class="field">
              <label>19. Telephone No.</label>
              <input v-model="formPersonal.telephone_no" placeholder="Landline or N/A" />
            </div>
            <div class="field">
              <label>20. Mobile No.</label>
              <input v-model="formPersonal.mobile_no" placeholder="09XX-XXX-XXXX" />
            </div>
            <div class="field">
              <label>21. Email Address</label>
              <input v-model="formPersonal.email_address" type="email" placeholder="official or personal email" />
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-save" :disabled="pdsStore.isSaving">
              {{ pdsStore.isSaving ? 'Saving...' : '💾 Save Section I Personal Info' }}
            </button>
          </div>
        </form>
      </div>

      <!-- ===================================================================== -->
      <!-- SECTION II: FAMILY BACKGROUND & CHILDREN (Items 22-25) -->
      <!-- ===================================================================== -->
      <div v-else-if="currentSection === 1" class="form-section">
        <div class="section-title-row">
          <div>
            <h3>II. Family Background (Items 22–25)</h3>
            <p class="section-sub">Spouse, Parents, and Children (Standard capacity: 12 children on C1; overflows to C7)</p>
          </div>
          <span class="sheet-indicator">Sheet C1 / C7</span>
        </div>

        <form @submit.prevent="saveFamily">
          <h4 class="sub-heading">22. Spouse Information</h4>
          <div class="form-grid-4">
            <div class="field">
              <label>Spouse Surname</label>
              <input v-model="formFamily.spouse_surname" placeholder="Surname or N/A" />
            </div>
            <div class="field">
              <label>First Name</label>
              <input v-model="formFamily.spouse_first_name" placeholder="First Name or N/A" />
            </div>
            <div class="field">
              <label>Middle Name</label>
              <input v-model="formFamily.spouse_middle_name" placeholder="Middle Name or N/A" />
            </div>
            <div class="field">
              <label>Name Extension</label>
              <input v-model="formFamily.spouse_name_extension" placeholder="JR., SR., III, etc." />
            </div>
          </div>

          <div class="form-grid-2">
            <div class="field">
              <label>Occupation</label>
              <input v-model="formFamily.spouse_occupation" placeholder="Occupation or N/A" />
            </div>
            <div class="field">
              <label>Employer / Business Name</label>
              <input v-model="formFamily.spouse_employer_business_name" placeholder="Company or N/A" />
            </div>
          </div>

          <div class="form-grid-2">
            <div class="field">
              <label>Business Address</label>
              <input v-model="formFamily.spouse_business_address" placeholder="Address or N/A" />
            </div>
            <div class="field">
              <label>Telephone No.</label>
              <input v-model="formFamily.spouse_telephone_no" placeholder="Tel No. or N/A" />
            </div>
          </div>

          <h4 class="sub-heading">Parents Information (Items 24–25)</h4>
          <div class="form-grid-4">
            <div class="field">
              <label>24. Father's Surname</label>
              <input v-model="formFamily.father_surname" placeholder="Surname" />
            </div>
            <div class="field">
              <label>First Name</label>
              <input v-model="formFamily.father_first_name" placeholder="First Name" />
            </div>
            <div class="field">
              <label>Middle Name</label>
              <input v-model="formFamily.father_middle_name" placeholder="Middle Name" />
            </div>
            <div class="field">
              <label>Name Extension</label>
              <input v-model="formFamily.father_name_extension" placeholder="JR., SR., etc." />
            </div>
          </div>

          <div class="form-grid-3">
            <div class="field">
              <label>25. Mother's Maiden Surname</label>
              <input v-model="formFamily.mother_surname" placeholder="Maiden Surname" />
            </div>
            <div class="field">
              <label>First Name</label>
              <input v-model="formFamily.mother_first_name" placeholder="First Name" />
            </div>
            <div class="field">
              <label>Middle Name</label>
              <input v-model="formFamily.mother_middle_name" placeholder="Middle Name" />
            </div>
          </div>

          <!-- Item 23: Children -->
          <div class="children-section">
            <div class="sub-header">
              <div>
                <h4 class="sub-heading" style="margin: 0;">23. Name of Children (List all)</h4>
                <p class="section-sub">Standard capacity: 12 rows on C1. More than 12 children automatically overflows to Sheet C7.</p>
              </div>
              <button type="button" @click="addChildRow" class="btn-add">+ Add Child</button>
            </div>

            <table class="sub-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Full Name of Child (First Name and Surname)</th>
                  <th>Date of Birth (dd/mm/yyyy)</th>
                  <th style="width: 80px;">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(ch, cIdx) in childrenList" :key="cIdx">
                  <td>{{ cIdx + 1 }}</td>
                  <td>
                    <input v-model="ch.name" required placeholder="Child's full name" />
                  </td>
                  <td>
                    <input v-model="ch.date_of_birth" type="date" />
                  </td>
                  <td>
                    <button type="button" @click="removeChildRow(cIdx)" class="btn-del">Delete</button>
                  </td>
                </tr>
                <tr v-if="!childrenList.length">
                  <td colspan="4" class="no-records">No children listed. Click '+ Add Child' if applicable.</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-save" :disabled="pdsStore.isSaving">
              {{ pdsStore.isSaving ? 'Saving...' : '💾 Save Section II Family Background' }}
            </button>
          </div>
        </form>
      </div>

      <!-- ===================================================================== -->
      <!-- SECTION III: EDUCATIONAL BACKGROUND (Item 26) -->
      <!-- ===================================================================== -->
      <div v-else-if="currentSection === 2" class="form-section">
        <div class="sub-header">
          <div>
            <h3>III. Educational Background (Item 26)</h3>
            <p class="section-sub">Elementary, Secondary, Vocational, College, Graduate Studies (Sheet C1 / C8 overflow)</p>
          </div>
          <button @click="openCreateModal('education')" class="btn-add">+ Add Education Record</button>
        </div>

        <table class="sub-table">
          <thead>
            <tr>
              <th>Level</th>
              <th>Name of School</th>
              <th>Basic Education / Degree / Course</th>
              <th>Period</th>
              <th>Units Earned</th>
              <th>Graduated</th>
              <th>Honors / Scholarship</th>
              <th style="width: 130px;">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="edu in pds.educational_backgrounds" :key="edu.id">
              <td><strong>{{ edu.level }}</strong></td>
              <td>{{ edu.school_name }}</td>
              <td>{{ edu.degree_course || 'N/A' }}</td>
              <td>{{ edu.from_year || '—' }} to {{ edu.to_year || '—' }}</td>
              <td>{{ edu.highest_level_units_earned || 'N/A' }}</td>
              <td>{{ edu.year_graduated || 'N/A' }}</td>
              <td>{{ edu.scholarship_academic_honors || 'N/A' }}</td>
              <td class="action-cell">
                <button @click="openEditModal('education', edu)" class="btn-edit">Edit</button>
                <button @click="deleteEdu(edu.id)" class="btn-del">Delete</button>
              </td>
            </tr>
            <tr v-if="!pds.educational_backgrounds?.length">
              <td colspan="8" class="no-records">No educational records yet.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- ===================================================================== -->
      <!-- SECTION IV: CIVIL SERVICE ELIGIBILITY (Item 27) -->
      <!-- ===================================================================== -->
      <div v-else-if="currentSection === 3" class="form-section">
        <div class="sub-header">
          <div>
            <h3>IV. Civil Service Eligibility (Item 27)</h3>
            <p class="section-sub">RA 1080 (Board/Bar), Career Service, PRC Licensure (Sheet C2 / C9 overflow)</p>
          </div>
          <button @click="openCreateModal('eligibility')" class="btn-add">+ Add Eligibility</button>
        </div>

        <table class="sub-table">
          <thead>
            <tr>
              <th>Eligibility Type</th>
              <th>Rating</th>
              <th>Exam Date</th>
              <th>Exam Place</th>
              <th>License No.</th>
              <th>Validity Date</th>
              <th style="width: 130px;">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cse in pds.civil_service_eligibilities" :key="cse.id">
              <td><strong>{{ cse.eligibility_type }}</strong></td>
              <td>{{ cse.rating || 'N/A' }}</td>
              <td>{{ formatDate(cse.examination_date) || 'N/A' }}</td>
              <td>{{ cse.examination_place || 'N/A' }}</td>
              <td>{{ cse.license_number || 'N/A' }}</td>
              <td>{{ formatDate(cse.license_validity_date) || 'N/A' }}</td>
              <td class="action-cell">
                <button @click="openEditModal('eligibility', cse)" class="btn-edit">Edit</button>
                <button @click="deleteCse(cse.id)" class="btn-del">Delete</button>
              </td>
            </tr>
            <tr v-if="!pds.civil_service_eligibilities?.length">
              <td colspan="7" class="no-records">No civil service eligibility entries recorded.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- ===================================================================== -->
      <!-- SECTION V: WORK EXPERIENCE (Item 28) -->
      <!-- ===================================================================== -->
      <div v-else-if="currentSection === 4" class="form-section">
        <div class="sub-header">
          <div>
            <h3>V. Work Experience (Item 28)</h3>
            <p class="section-sub">Teaching assignments, previous schools, and private practice (Sheet C2 / C6 overflow)</p>
          </div>
          <button @click="openCreateModal('work')" class="btn-add">+ Add Work Record</button>
        </div>

        <table class="sub-table">
          <thead>
            <tr>
              <th>Position Title</th>
              <th>Department / Agency / Company</th>
              <th>Inclusive Dates</th>
              <th>Monthly Salary</th>
              <th>Pay Grade</th>
              <th>Status</th>
              <th>Gov't?</th>
              <th style="width: 130px;">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="we in pds.work_experiences" :key="we.id">
              <td><strong>{{ we.position_title }}</strong></td>
              <td>{{ we.department_agency_company }}</td>
              <td>{{ formatDate(we.from_date) }} to {{ we.to_present ? 'Present' : formatDate(we.to_date) }}</td>
              <td>{{ we.monthly_salary ? '₱' + we.monthly_salary : 'N/A' }}</td>
              <td>{{ we.salary_grade || 'N/A' }}</td>
              <td>{{ we.appointment_status || 'N/A' }}</td>
              <td>{{ we.is_government_service ? 'Yes' : 'No' }}</td>
              <td class="action-cell">
                <button @click="openEditModal('work', we)" class="btn-edit">Edit</button>
                <button @click="deleteWe(we.id)" class="btn-del">Delete</button>
              </td>
            </tr>
            <tr v-if="!pds.work_experiences?.length">
              <td colspan="8" class="no-records">No work experience entries recorded.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- ===================================================================== -->
      <!-- SECTION VI: LEARNING & DEVELOPMENT (Item 29) -->
      <!-- ===================================================================== -->
      <div v-else-if="currentSection === 5" class="form-section">
        <div class="sub-header">
          <div>
            <h3>VI. Learning &amp; Development (Item 29)</h3>
            <p class="section-sub">Seminars, INSET, CPD Trainings, and Certifications (Sheet C3 / C5 overflow)</p>
          </div>
          <button @click="openCreateModal('ld')" class="btn-add">+ Add Training</button>
        </div>

        <table class="sub-table">
          <thead>
            <tr>
              <th>Title of Learning &amp; Development</th>
              <th>Inclusive Dates</th>
              <th>Hours</th>
              <th>Type of L&amp;D</th>
              <th>Conducted / Sponsored By</th>
              <th style="width: 130px;">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ld in pds.learning_developments" :key="ld.id">
              <td><strong>{{ ld.training_title }}</strong></td>
              <td>{{ formatDate(ld.from_date) }} to {{ formatDate(ld.to_date) }}</td>
              <td><strong>{{ ld.number_of_hours }} hrs</strong></td>
              <td><span class="type-pill">{{ ld.ld_type || 'General' }}</span></td>
              <td>{{ ld.conducted_sponsored_by }}</td>
              <td class="action-cell">
                <button @click="openEditModal('ld', ld)" class="btn-edit">Edit</button>
                <button @click="deleteLd(ld.id)" class="btn-del">Delete</button>
              </td>
            </tr>
            <tr v-if="!pds.learning_developments?.length">
              <td colspan="6" class="no-records">No L&amp;D trainings entered.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- ===================================================================== -->
      <!-- SECTION VII: VOLUNTARY WORK (Item 30) -->
      <!-- ===================================================================== -->
      <div v-else-if="currentSection === 6" class="form-section">
        <div class="sub-header">
          <div>
            <h3>VII. Voluntary Work / Civic Involvement (Item 30)</h3>
            <p class="section-sub">Civic, Non-Government, People, or Voluntary Organizations (Sheet C3 / C10 overflow)</p>
          </div>
          <button @click="openCreateModal('voluntary')" class="btn-add">+ Add Voluntary Work</button>
        </div>

        <table class="sub-table">
          <thead>
            <tr>
              <th>Name &amp; Address of Organization</th>
              <th>Inclusive Dates</th>
              <th>Hours</th>
              <th>Position / Nature of Work</th>
              <th style="width: 130px;">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="vw in pds.voluntary_works" :key="vw.id">
              <td><strong>{{ vw.organization_name_address }}</strong></td>
              <td>{{ formatDate(vw.from_date) }} to {{ formatDate(vw.to_date) }}</td>
              <td>{{ vw.number_of_hours }} hrs</td>
              <td>{{ vw.position_nature_of_work }}</td>
              <td class="action-cell">
                <button @click="openEditModal('voluntary', vw)" class="btn-edit">Edit</button>
                <button @click="deleteVw(vw.id)" class="btn-del">Delete</button>
              </td>
            </tr>
            <tr v-if="!pds.voluntary_works?.length">
              <td colspan="5" class="no-records">No voluntary work records logged.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- ===================================================================== -->
      <!-- SECTION VIII: OTHER INFORMATION (Items 31–33) -->
      <!-- ===================================================================== -->
      <div v-else-if="currentSection === 7" class="form-section">
        <div class="section-title-row">
          <div>
            <h3>VIII. Other Information (Items 31–33)</h3>
            <p class="section-sub">Special Skills, Non-Academic Distinctions, and Organization Memberships (Sheet C3 / C11 overflow)</p>
          </div>
          <span class="sheet-indicator">Sheet C3 / C11</span>
        </div>

        <form @submit.prevent="saveOtherInformation">
          <div class="form-grid-3">
            <!-- 31. Special Skills & Hobbies -->
            <div class="other-info-card glass-panel">
              <h4>31. Special Skills &amp; Hobbies</h4>
              <p class="field-help">Press Enter or Add to register each skill</p>
              <div class="add-tag-row">
                <input v-model="newSkill" @keyup.enter.prevent="addTag('skills')" placeholder="e.g. Piano, Coding..." />
                <button type="button" @click="addTag('skills')" class="btn-tag-add">+</button>
              </div>
              <div class="tags-container">
                <span v-for="(s, idx) in otherInfoForm.special_skills_hobbies" :key="idx" class="info-tag">
                  {{ s }}
                  <button type="button" @click="removeTag('skills', idx)" class="tag-remove">×</button>
                </span>
                <span v-if="!otherInfoForm.special_skills_hobbies?.length" class="empty-tag-text">None added (N/A)</span>
              </div>
            </div>

            <!-- 32. Non-Academic Distinctions -->
            <div class="other-info-card glass-panel">
              <h4>32. Non-Academic Distinctions</h4>
              <p class="field-help">Awards, recognitions (Write in full)</p>
              <div class="add-tag-row">
                <input v-model="newDistinction" @keyup.enter.prevent="addTag('distinctions')" placeholder="e.g. Outstanding Educator..." />
                <button type="button" @click="addTag('distinctions')" class="btn-tag-add">+</button>
              </div>
              <div class="tags-container">
                <span v-for="(d, idx) in otherInfoForm.non_academic_distinctions" :key="idx" class="info-tag">
                  {{ d }}
                  <button type="button" @click="removeTag('distinctions', idx)" class="tag-remove">×</button>
                </span>
                <span v-if="!otherInfoForm.non_academic_distinctions?.length" class="empty-tag-text">None added (N/A)</span>
              </div>
            </div>

            <!-- 33. Memberships -->
            <div class="other-info-card glass-panel">
              <h4>33. Memberships in Organizations</h4>
              <p class="field-help">Write full association/organization name</p>
              <div class="add-tag-row">
                <input v-model="newMembership" @keyup.enter.prevent="addTag('memberships')" placeholder="e.g. Philippine Normal Alumni..." />
                <button type="button" @click="addTag('memberships')" class="btn-tag-add">+</button>
              </div>
              <div class="tags-container">
                <span v-for="(m, idx) in otherInfoForm.organization_memberships" :key="idx" class="info-tag">
                  {{ m }}
                  <button type="button" @click="removeTag('memberships', idx)" class="tag-remove">×</button>
                </span>
                <span v-if="!otherInfoForm.organization_memberships?.length" class="empty-tag-text">None added (N/A)</span>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-save" :disabled="pdsStore.isSaving">
              {{ pdsStore.isSaving ? 'Saving...' : '💾 Save Section VIII Other Information' }}
            </button>
          </div>
        </form>
      </div>

      <!-- ===================================================================== -->
      <!-- SECTION IX: GOVERNMENT QUESTIONS (Items 34–40) -->
      <!-- ===================================================================== -->
      <div v-else-if="currentSection === 8" class="form-section">
        <div class="section-title-row">
          <div>
            <h3>IX. Statutory &amp; Government Questions (Items 34–40)</h3>
            <p class="section-sub">Statutory background disclosures required by Philippine Civil Service Law</p>
          </div>
          <span class="sheet-indicator">Sheet C4</span>
        </div>

        <form @submit.prevent="saveGovernmentQuestions">
          <!-- 34 -->
          <div class="question-card glass-panel">
            <p class="question-text">
              <strong>34.</strong> Are you related by consanguinity or affinity to the appointing or recommending authority, or to chief of bureau or office or person exercising immediate supervision?
            </p>
            <div class="question-item">
              <label>a. Within the third degree (for National Government employees)?</label>
              <div class="radio-options">
                <label><input type="radio" :value="true" v-model="govQuestionsForm.q34a_related_third_degree" /> Yes</label>
                <label><input type="radio" :value="false" v-model="govQuestionsForm.q34a_related_third_degree" /> No</label>
              </div>
              <div v-if="govQuestionsForm.q34a_related_third_degree" class="mt-2">
                <input v-model="govQuestionsForm.q34a_details" placeholder="If YES, give details..." />
              </div>
            </div>
            <div class="question-item mt-3">
              <label>b. Within the fourth degree (for Local Government employees)?</label>
              <div class="radio-options">
                <label><input type="radio" :value="true" v-model="govQuestionsForm.q34b_related_fourth_degree" /> Yes</label>
                <label><input type="radio" :value="false" v-model="govQuestionsForm.q34b_related_fourth_degree" /> No</label>
              </div>
              <div v-if="govQuestionsForm.q34b_related_fourth_degree" class="mt-2">
                <input v-model="govQuestionsForm.q34b_details" placeholder="If YES, give details..." />
              </div>
            </div>
          </div>

          <!-- 35 -->
          <div class="question-card glass-panel">
            <p class="question-text"><strong>35.</strong> Administrative and Criminal Disclosures</p>
            <div class="question-item">
              <label>a. Have you ever been found guilty of any administrative offense?</label>
              <div class="radio-options">
                <label><input type="radio" :value="true" v-model="govQuestionsForm.q35a_admin_offense" /> Yes</label>
                <label><input type="radio" :value="false" v-model="govQuestionsForm.q35a_admin_offense" /> No</label>
              </div>
              <div v-if="govQuestionsForm.q35a_admin_offense" class="mt-2">
                <input v-model="govQuestionsForm.q35a_details" placeholder="If YES, give details..." />
              </div>
            </div>
            <div class="question-item mt-3">
              <label>b. Have you been criminally charged before any court?</label>
              <div class="radio-options">
                <label><input type="radio" :value="true" v-model="govQuestionsForm.q35b_criminal_charged" /> Yes</label>
                <label><input type="radio" :value="false" v-model="govQuestionsForm.q35b_criminal_charged" /> No</label>
              </div>
              <div v-if="govQuestionsForm.q35b_criminal_charged" class="form-grid-3 mt-2">
                <input v-model="govQuestionsForm.q35b_date_filed" type="date" placeholder="Date Filed" />
                <input v-model="govQuestionsForm.q35b_status" placeholder="Status of Case" />
                <input v-model="govQuestionsForm.q35b_details" placeholder="Details of charge..." />
              </div>
            </div>
          </div>

          <!-- 36 -->
          <div class="question-card glass-panel">
            <div class="question-item">
              <label><strong>36.</strong> Have you ever been convicted of any crime or violation of any law, decree, ordinance or regulation by any court or tribunal?</label>
              <div class="radio-options">
                <label><input type="radio" :value="true" v-model="govQuestionsForm.q36_convicted" /> Yes</label>
                <label><input type="radio" :value="false" v-model="govQuestionsForm.q36_convicted" /> No</label>
              </div>
              <div v-if="govQuestionsForm.q36_convicted" class="mt-2">
                <input v-model="govQuestionsForm.q36_details" placeholder="If YES, give details..." />
              </div>
            </div>
          </div>

          <!-- 37 -->
          <div class="question-card glass-panel">
            <div class="question-item">
              <label><strong>37.</strong> Have you ever been separated from the service in any mode (resignation, retirement, dropped from rolls, dismissal, termination, phased out)?</label>
              <div class="radio-options">
                <label><input type="radio" :value="true" v-model="govQuestionsForm.q37_separated_service" /> Yes</label>
                <label><input type="radio" :value="false" v-model="govQuestionsForm.q37_separated_service" /> No</label>
              </div>
              <div v-if="govQuestionsForm.q37_separated_service" class="mt-2">
                <input v-model="govQuestionsForm.q37_details" placeholder="If YES, give details..." />
              </div>
            </div>
          </div>

          <!-- 38 -->
          <div class="question-card glass-panel">
            <p class="question-text"><strong>38.</strong> Election Disclosures</p>
            <div class="question-item">
              <label>a. Have you ever been a candidate in a national or local election held within the last year (except Barangay election)?</label>
              <div class="radio-options">
                <label><input type="radio" :value="true" v-model="govQuestionsForm.q38a_candidate_election" /> Yes</label>
                <label><input type="radio" :value="false" v-model="govQuestionsForm.q38a_candidate_election" /> No</label>
              </div>
              <div v-if="govQuestionsForm.q38a_candidate_election" class="mt-2">
                <input v-model="govQuestionsForm.q38a_details" placeholder="If YES, give details..." />
              </div>
            </div>
            <div class="question-item mt-3">
              <label>b. Have you resigned from government service during 3-month period before election to campaign for a candidate?</label>
              <div class="radio-options">
                <label><input type="radio" :value="true" v-model="govQuestionsForm.q38b_resigned_campaign" /> Yes</label>
                <label><input type="radio" :value="false" v-model="govQuestionsForm.q38b_resigned_campaign" /> No</label>
              </div>
              <div v-if="govQuestionsForm.q38b_resigned_campaign" class="mt-2">
                <input v-model="govQuestionsForm.q38b_details" placeholder="If YES, give details..." />
              </div>
            </div>
          </div>

          <!-- 39 -->
          <div class="question-card glass-panel">
            <div class="question-item">
              <label><strong>39.</strong> Have you acquired the status of an immigrant or permanent resident of another country?</label>
              <div class="radio-options">
                <label><input type="radio" :value="true" v-model="govQuestionsForm.q39_immigrant_permanent_resident" /> Yes</label>
                <label><input type="radio" :value="false" v-model="govQuestionsForm.q39_immigrant_permanent_resident" /> No</label>
              </div>
              <div v-if="govQuestionsForm.q39_immigrant_permanent_resident" class="mt-2">
                <input v-model="govQuestionsForm.q39_country" placeholder="If YES, indicate country..." />
              </div>
            </div>
          </div>

          <!-- 40 -->
          <div class="question-card glass-panel">
            <p class="question-text"><strong>40.</strong> Pursuant to Special Social Legislation</p>
            <div class="question-item">
              <label>a. Are you a member of any indigenous group?</label>
              <div class="radio-options">
                <label><input type="radio" :value="true" v-model="govQuestionsForm.q40a_indigenous_group" /> Yes</label>
                <label><input type="radio" :value="false" v-model="govQuestionsForm.q40a_indigenous_group" /> No</label>
              </div>
              <div v-if="govQuestionsForm.q40a_indigenous_group" class="mt-2">
                <input v-model="govQuestionsForm.q40a_specify" placeholder="If YES, please specify..." />
              </div>
            </div>
            <div class="question-item mt-3">
              <label>b. Are you a person with disability?</label>
              <div class="radio-options">
                <label><input type="radio" :value="true" v-model="govQuestionsForm.q40b_person_with_disability" /> Yes</label>
                <label><input type="radio" :value="false" v-model="govQuestionsForm.q40b_person_with_disability" /> No</label>
              </div>
              <div v-if="govQuestionsForm.q40b_person_with_disability" class="mt-2">
                <input v-model="govQuestionsForm.q40b_id_number" placeholder="If YES, please specify PWD ID No...." />
              </div>
            </div>
            <div class="question-item mt-3">
              <label>c. Are you a solo parent?</label>
              <div class="radio-options">
                <label><input type="radio" :value="true" v-model="govQuestionsForm.q40c_solo_parent" /> Yes</label>
                <label><input type="radio" :value="false" v-model="govQuestionsForm.q40c_solo_parent" /> No</label>
              </div>
              <div v-if="govQuestionsForm.q40c_solo_parent" class="mt-2">
                <input v-model="govQuestionsForm.q40c_id_number" placeholder="If YES, please specify Solo Parent ID No...." />
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-save" :disabled="pdsStore.isSaving">
              {{ pdsStore.isSaving ? 'Saving...' : '💾 Save Items 34–40 Disclosures' }}
            </button>
          </div>
        </form>
      </div>

      <!-- ===================================================================== -->
      <!-- ===================================================================== -->
      <!-- SECTION X: REFERENCES (Item 41) & ITEM 42 DECLARATION -->
      <!-- ===================================================================== -->
      <div v-else-if="currentSection === 9" class="form-section">
        <div class="sub-header">
          <div>
            <h3>X. References (Item 41)</h3>
            <p class="section-sub">Persons not related by consanguinity or affinity to applicant/appointee (Sheet C4)</p>
          </div>
          <button @click="openCreateModal('reference')" class="btn-add">+ Add Reference</button>
        </div>

        <table class="sub-table">
          <thead>
            <tr>
              <th>Full Name (First Name, MI, Surname)</th>
              <th>Office / Residential Address</th>
              <th>Contact No. / Email</th>
              <th style="width: 130px;">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ref in pds.references" :key="ref.id">
              <td><strong>{{ ref.name }}</strong></td>
              <td>{{ ref.office_residential_address }}</td>
              <td>{{ ref.contact_no_email }}</td>
              <td class="action-cell">
                <button @click="openEditModal('reference', ref)" class="btn-edit">Edit</button>
                <button @click="deleteRef(ref.id)" class="btn-del">Delete</button>
              </td>
            </tr>
            <tr v-if="!pds.references?.length">
              <td colspan="4" class="no-records">No character references recorded (provide at least 3 references).</td>
            </tr>
          </tbody>
        </table>

        <!-- Sheet C4 Completion Divider Banner -->
        <div class="c4-completion-banner">
          <div>
            <h4>Sheet C4 Finalization • Item 42 Sworn Oath &amp; Signatures</h4>
            <p class="section-sub">Affix your 4.5 cm x 3.5 cm digital picture, electronic signature, government ID, and oath administering details</p>
          </div>
          <span class="sheet-indicator">Sheet C4 • Page 4</span>
        </div>

        <!-- Comprehensive Item 42 Form -->
        <form @submit.prevent="saveDeclaration" class="item42-container">
          <!-- 42. Oath Statement -->
          <div class="declaration-oath-card">
            <div class="oath-title-bar">
              <span class="oath-badge">CSC Form 212 • Item 42</span>
              <h4 class="oath-heading">42. I DECLARE UNDER OATH</h4>
            </div>
            <p class="oath-full-text">
              I declare under oath that I have personally accomplished this Personal Data Sheet which is a true,
              correct, and complete statement pursuant to the provisions of pertinent laws, rules, and regulations
              of the Republic of the Philippines. I authorize the agency head/authorized representative to verify/validate
              the contents stated herein. I agree that any misrepresentation made in this document and its attachments
              shall cause the filing of administrative/criminal case/s against me.
            </p>
          </div>

          <!-- 3-Column Execution Grid: Gov ID | Signature Box | Passport Photo & Thumbmark -->
          <div class="item42-execution-grid">
            
            <!-- Col 1: Government Issued Identification -->
            <div class="execution-col gov-id-card glass-panel">
              <div class="col-header">
                <h5>Government Issued ID</h5>
                <p class="col-sub">Passport, GSIS, SSS, PRC, Driver's License, PhilID, etc.</p>
              </div>
              <div class="field">
                <label>Government Issued ID Type *</label>
                <input v-model="formDecl.government_id_type" placeholder="e.g. PRC License, Passport, GSIS UMID" required />
              </div>
              <div class="field">
                <label>ID / License / Passport No. *</label>
                <input v-model="formDecl.id_license_passport_no" placeholder="e.g. PRC-0123456" required />
              </div>
              <div class="field">
                <label>Date &amp; Place of Issuance</label>
                <input v-model="formDecl.date_place_of_issuance" placeholder="e.g. Manila, Philippines / 12/04/2021" />
              </div>
              <div class="field">
                <label>Date Accomplished *</label>
                <input v-model="formDecl.date_accomplished" type="date" required />
              </div>
            </div>

            <!-- Col 2: Signature Box ("Signature (Sign inside the box)") -->
            <div class="execution-col signature-card glass-panel">
              <div class="col-header">
                <h5>Affiant Signature</h5>
                <span class="badge-e-sig">(e-signature / digital certificate)</span>
              </div>
              <div class="signature-box-container">
                <div class="sign-inside-box">
                  <div v-if="pds.signature_url" class="signature-img-container">
                    <img :src="pds.signature_url" alt="Attached E-Signature" class="attached-sig-img" />
                    <div class="sig-affiant-caption">{{ pds.user?.full_name }}</div>
                  </div>
                  <div v-else class="signature-script-placeholder">
                    <div class="signature-line">
                      <span class="signature-script">{{ pds.user?.full_name }}</span>
                    </div>
                    <div class="e-cert-tag">
                      <span class="cert-icon">🛡️</span> Digitally Certified E-Signature
                    </div>
                  </div>
                </div>
                <div class="sign-box-caption">Signature (Sign inside the box)</div>

                <!-- Signature Attachment Controls -->
                <div class="sig-action-buttons">
                  <button type="button" @click="showSignatureModal = true" class="btn-sig-action btn-draw-sig">
                    ✍️ {{ pds.signature_url ? 'Re-draw' : 'Draw E-Sig' }}
                  </button>
                  <button type="button" @click="triggerSignatureUpload" class="btn-sig-action btn-upload-sig" :disabled="isUploadingSignature">
                    📁 {{ isUploadingSignature ? 'Uploading...' : 'Upload Image' }}
                  </button>
                  <button v-if="pds.signature_url" type="button" @click="removeAttachedSignature" class="btn-sig-action btn-remove-sig" title="Remove signature">
                    ✕
                  </button>
                </div>
              </div>

              <div class="field mt-3">
                <label>Signature Authentication Mode</label>
                <select v-model="formDecl.signature_type">
                  <option value="e-signature/digital certificate">e-signature / Digital Certificate (RA 8792)</option>
                  <option value="Wet Signature Upon Printing">Physical Wet Signature (Sign after printing)</option>
                </select>
              </div>

              <div class="signature-legal-note">
                Pursuant to Republic Act No. 8792 (Electronic Commerce Act of 2000), electronic signatures and digital certificates carry full legal validity.
              </div>
            </div>

            <!-- Col 3: Passport Photo Affixing (4.5 x 3.5 cm) & Right Thumbmark -->
            <div class="execution-col photo-thumb-card glass-panel">
              <div class="col-header">
                <h5>Digital Picture &amp; Thumbmark</h5>
                <p class="col-sub">Passport size 4.5 cm x 3.5 cm &amp; Right Thumbmark</p>
              </div>

              <div class="photo-thumb-dual">
                <!-- Passport Photo Frame -->
                <div class="passport-photo-wrapper">
                  <div class="passport-photo-frame">
                    <img v-if="pds.photo_url" :src="pds.photo_url" alt="Affixed Passport Photo" class="passport-img" />
                    <div v-else class="passport-placeholder">
                      <div class="photo-icon">📷</div>
                      <strong>PHOTO</strong>
                      <span class="photo-dims">4.5 cm x 3.5 cm</span>
                      <span class="photo-note">Passport size within last 6 mos.</span>
                    </div>
                  </div>
                  <div class="photo-actions">
                    <button type="button" @click="triggerPhotoUpload" class="btn-photo-upload" :disabled="isUploadingPhoto">
                      {{ isUploadingPhoto ? 'Uploading...' : (pds.photo_url ? '🔄 Replace' : '📁 Affix Photo') }}
                    </button>
                    <button v-if="pds.photo_url" type="button" @click="removeAffixedPhoto" class="btn-photo-remove" title="Remove photo">
                      ✕
                    </button>
                  </div>
                </div>

                <!-- Right Thumbmark Frame -->
                <div class="thumbmark-wrapper">
                  <div class="thumbmark-frame" :class="{ affixed: formDecl.has_thumbmark }">
                    <div class="thumb-icon">👆</div>
                    <div class="thumb-title">Right Thumbmark</div>
                    <div class="thumb-status">{{ formDecl.has_thumbmark ? 'Affixed / Verified' : '(If unable to sign)' }}</div>
                  </div>
                  <label class="cb-thumbmark">
                    <input type="checkbox" v-model="formDecl.has_thumbmark" />
                    <span>Unable to sign (Affix Thumbmark)</span>
                  </label>
                </div>
              </div>
              <p class="photo-disclaimer">
                * Note: Computer generated or photocopied pictures are not acceptable as per CSC guidelines.
              </p>
            </div>
          </div>

          <!-- Section: Jurat & Person Administering Oath -->
          <div class="jurat-card glass-panel mt-4">
            <div class="jurat-header">
              <h5>SUBSCRIBED AND SWORN TO (Jurat / Oath Administration)</h5>
              <span class="jurat-sub">(e-signature / digital certificate except for notary public)</span>
            </div>
            <p class="jurat-statement">
              "SUBSCRIBED AND SWORN to before me this 
              <strong>{{ formDecl.subscribed_date || '_________________________' }}</strong>, 
              affiant exhibiting his/her validly issued government ID as indicated above."
            </p>

            <div class="form-grid-3">
              <div class="field">
                <label>Subscribed Date &amp; Place</label>
                <input v-model="formDecl.subscribed_date" placeholder="e.g. 23rd day of September 2026, Tuguegarao City" />
              </div>
              <div class="field">
                <label>Person Administering Oath (Name)</label>
                <input v-model="formDecl.administering_officer_name" placeholder="e.g. ATTY. JUAN DELA CRUZ" />
              </div>
              <div class="field">
                <label>Designation / Position / Title</label>
                <input v-model="formDecl.administering_officer_title" placeholder="e.g. Administrative Officer V / Notary Public" />
              </div>
            </div>
            <div class="form-grid-1">
              <div class="field">
                <label>Office / Agency / Notary Commission Details</label>
                <input v-model="formDecl.administering_officer_office" placeholder="e.g. CES / DepEd / Commission No. 2026-01" />
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-save" :disabled="pdsStore.isSaving">
              {{ pdsStore.isSaving ? 'Saving...' : '💾 Save Item 42 Declaration & Identification' }}
            </button>
          </div>
        </form>
      </div>

      <!-- ===================================================================== -->
      <!-- SECTION XI: DECLARATION, GOVERNMENT ID & OATH (Item 42) -->
      <!-- ===================================================================== -->
      <div v-else-if="currentSection === 10" class="form-section">
        <div class="section-title-row">
          <div>
            <h3>XI. Declaration, Government ID &amp; Oath (Item 42)</h3>
            <p class="section-sub">Sworn affidavit, passport photo affixing, and signature box compliance under Civil Service Law</p>
          </div>
          <span class="sheet-indicator">Sheet C4</span>
        </div>

        <form @submit.prevent="saveDeclaration" class="item42-container">
          <!-- 42. Oath Statement -->
          <div class="declaration-oath-card">
            <div class="oath-title-bar">
              <span class="oath-badge">CSC Form 212 • Item 42</span>
              <h4 class="oath-heading">42. I DECLARE UNDER OATH</h4>
            </div>
            <p class="oath-full-text">
              I declare under oath that I have personally accomplished this Personal Data Sheet which is a true,
              correct, and complete statement pursuant to the provisions of pertinent laws, rules, and regulations
              of the Republic of the Philippines. I authorize the agency head/authorized representative to verify/validate
              the contents stated herein. I agree that any misrepresentation made in this document and its attachments
              shall cause the filing of administrative/criminal case/s against me.
            </p>
          </div>

          <!-- 3-Column Execution Grid: Gov ID | Signature Box | Passport Photo & Thumbmark -->
          <div class="item42-execution-grid">
            
            <!-- Col 1: Government Issued Identification -->
            <div class="execution-col gov-id-card glass-panel">
              <div class="col-header">
                <h5>Government Issued ID</h5>
                <p class="col-sub">Passport, GSIS, SSS, PRC, Driver's License, PhilID, etc.</p>
              </div>
              <div class="field">
                <label>Government Issued ID Type *</label>
                <input v-model="formDecl.government_id_type" placeholder="e.g. PRC License, Passport, GSIS UMID" required />
              </div>
              <div class="field">
                <label>ID / License / Passport No. *</label>
                <input v-model="formDecl.id_license_passport_no" placeholder="e.g. PRC-0123456" required />
              </div>
              <div class="field">
                <label>Date &amp; Place of Issuance</label>
                <input v-model="formDecl.date_place_of_issuance" placeholder="e.g. Manila, Philippines / 12/04/2021" />
              </div>
              <div class="field">
                <label>Date Accomplished *</label>
                <input v-model="formDecl.date_accomplished" type="date" required />
              </div>
            </div>

            <!-- Col 2: Signature Box ("Signature (Sign inside the box)") -->
            <div class="execution-col signature-card glass-panel">
              <div class="col-header">
                <h5>Affiant Signature</h5>
                <span class="badge-e-sig">(e-signature / digital certificate)</span>
              </div>
              <div class="signature-box-container">
                <div class="sign-inside-box">
                  <div v-if="pds.signature_url" class="signature-img-container">
                    <img :src="pds.signature_url" alt="Attached E-Signature" class="attached-sig-img" />
                    <div class="sig-affiant-caption">{{ pds.user?.full_name }}</div>
                  </div>
                  <div v-else class="signature-script-placeholder">
                    <div class="signature-line">
                      <span class="signature-script">{{ pds.user?.full_name }}</span>
                    </div>
                    <div class="e-cert-tag">
                      <span class="cert-icon">🛡️</span> Digitally Certified E-Signature
                    </div>
                  </div>
                </div>
                <div class="sign-box-caption">Signature (Sign inside the box)</div>

                <!-- Signature Attachment Controls -->
                <div class="sig-action-buttons">
                  <button type="button" @click="showSignatureModal = true" class="btn-sig-action btn-draw-sig">
                    ✍️ {{ pds.signature_url ? 'Re-draw' : 'Draw E-Sig' }}
                  </button>
                  <button type="button" @click="triggerSignatureUpload" class="btn-sig-action btn-upload-sig" :disabled="isUploadingSignature">
                    📁 {{ isUploadingSignature ? 'Uploading...' : 'Upload Image' }}
                  </button>
                  <button v-if="pds.signature_url" type="button" @click="removeAttachedSignature" class="btn-sig-action btn-remove-sig" title="Remove signature">
                    ✕
                  </button>
                </div>
              </div>

              <div class="field mt-3">
                <label>Signature Authentication Mode</label>
                <select v-model="formDecl.signature_type">
                  <option value="e-signature/digital certificate">e-signature / Digital Certificate (RA 8792)</option>
                  <option value="Wet Signature Upon Printing">Physical Wet Signature (Sign after printing)</option>
                </select>
              </div>

              <div class="signature-legal-note">
                Pursuant to Republic Act No. 8792 (Electronic Commerce Act of 2000), electronic signatures and digital certificates carry full legal validity.
              </div>
            </div>

            <!-- Col 3: Passport Photo Affixing (4.5 x 3.5 cm) & Right Thumbmark -->
            <div class="execution-col photo-thumb-card glass-panel">
              <div class="col-header">
                <h5>Digital Picture &amp; Thumbmark</h5>
                <p class="col-sub">Passport size 4.5 cm x 3.5 cm &amp; Right Thumbmark</p>
              </div>

              <div class="photo-thumb-dual">
                <!-- Passport Photo Frame -->
                <div class="passport-photo-wrapper">
                  <div class="passport-photo-frame">
                    <img v-if="pds.photo_url" :src="pds.photo_url" alt="Affixed Passport Photo" class="passport-img" />
                    <div v-else class="passport-placeholder">
                      <div class="photo-icon">📷</div>
                      <strong>PHOTO</strong>
                      <span class="photo-dims">4.5 cm x 3.5 cm</span>
                      <span class="photo-note">Passport size within last 6 mos.</span>
                    </div>
                  </div>
                  <div class="photo-actions">
                    <button type="button" @click="triggerPhotoUpload" class="btn-photo-upload" :disabled="isUploadingPhoto">
                      {{ isUploadingPhoto ? 'Uploading...' : (pds.photo_url ? '🔄 Replace' : '📁 Affix Photo') }}
                    </button>
                    <button v-if="pds.photo_url" type="button" @click="removeAffixedPhoto" class="btn-photo-remove" title="Remove photo">
                      ✕
                    </button>
                  </div>
                </div>

                <!-- Right Thumbmark Frame -->
                <div class="thumbmark-wrapper">
                  <div class="thumbmark-frame" :class="{ affixed: formDecl.has_thumbmark }">
                    <div class="thumb-icon">👆</div>
                    <div class="thumb-title">Right Thumbmark</div>
                    <div class="thumb-status">{{ formDecl.has_thumbmark ? 'Affixed / Verified' : '(If unable to sign)' }}</div>
                  </div>
                  <label class="cb-thumbmark">
                    <input type="checkbox" v-model="formDecl.has_thumbmark" />
                    <span>Unable to sign (Affix Thumbmark)</span>
                  </label>
                </div>
              </div>
              <p class="photo-disclaimer">
                * Note: Computer generated or photocopied pictures are not acceptable as per CSC guidelines.
              </p>
            </div>
          </div>

          <!-- Section: Jurat & Person Administering Oath -->
          <div class="jurat-card glass-panel mt-4">
            <div class="jurat-header">
              <h5>SUBSCRIBED AND SWORN TO (Jurat / Oath Administration)</h5>
              <span class="jurat-sub">(e-signature / digital certificate except for notary public)</span>
            </div>
            <p class="jurat-statement">
              "SUBSCRIBED AND SWORN to before me this 
              <strong>{{ formDecl.subscribed_date || '_________________________' }}</strong>, 
              affiant exhibiting his/her validly issued government ID as indicated above."
            </p>

            <div class="form-grid-3">
              <div class="field">
                <label>Subscribed Date &amp; Place</label>
                <input v-model="formDecl.subscribed_date" placeholder="e.g. 23rd day of September 2026, Tuguegarao City" />
              </div>
              <div class="field">
                <label>Person Administering Oath (Name)</label>
                <input v-model="formDecl.administering_officer_name" placeholder="e.g. ATTY. JUAN DELA CRUZ" />
              </div>
              <div class="field">
                <label>Designation / Position / Title</label>
                <input v-model="formDecl.administering_officer_title" placeholder="e.g. Administrative Officer V / Notary Public" />
              </div>
            </div>
            <div class="form-grid-1">
              <div class="field">
                <label>Office / Agency / Notary Commission Details</label>
                <input v-model="formDecl.administering_officer_office" placeholder="e.g. CES / DepEd / Commission No. 2026-01" />
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-save" :disabled="pdsStore.isSaving">
              {{ pdsStore.isSaving ? 'Saving...' : '💾 Save Item 42 Declaration & Identification' }}
            </button>
          </div>
        </form>
      </div>

    </div>

    <!-- ===================================================================== -->
    <!-- UNIFIED SUB-MODAL FOR CREATE / EDIT -->
    <!-- ===================================================================== -->
    <div v-if="activeModal" class="modal-backdrop" @click.self="activeModal = null">
      <div class="modal-card glass-panel">
        <!-- Education Modal -->
        <div v-if="activeModal === 'education'">
          <h3>{{ editingItemId ? 'Edit Educational Background' : 'Add Educational Background' }}</h3>
          <p class="modal-sub">CSC Form 212 Item 26 — DO NOT ABBREVIATE school names.</p>
          <form @submit.prevent="submitEdu">
            <div class="field">
              <label>Level *</label>
              <select v-model="modalEdu.level" required>
                <option value="Elementary">Elementary</option>
                <option value="Secondary">Secondary</option>
                <option value="Vocational/Trade Course">Vocational/Trade Course</option>
                <option value="College">College</option>
                <option value="Graduate Studies">Graduate Studies</option>
              </select>
            </div>
            <div class="field">
              <label>Name of School * (Write in full)</label>
              <input v-model="modalEdu.school_name" required placeholder="e.g. Philippine Normal University" />
            </div>
            <div class="field">
              <label>Basic Education / Degree / Course (Write in full)</label>
              <input v-model="modalEdu.degree_course" placeholder="e.g. Bachelor of Secondary Education Major in English" />
            </div>
            <div class="form-grid-2">
              <div class="field">
                <label>Period of Attendance (From Year)</label>
                <input v-model="modalEdu.from_year" placeholder="e.g. 2018" />
              </div>
              <div class="field">
                <label>Period of Attendance (To Year)</label>
                <input v-model="modalEdu.to_year" placeholder="e.g. 2022" />
              </div>
            </div>
            <div class="form-grid-2">
              <div class="field">
                <label>Highest Level / Units Earned (if not graduated)</label>
                <input v-model="modalEdu.highest_level_units_earned" placeholder="e.g. 48 units" />
              </div>
              <div class="field">
                <label>Year Graduated (if graduated)</label>
                <input v-model="modalEdu.year_graduated" placeholder="e.g. 2022" />
              </div>
            </div>
            <div class="field">
              <label>Scholarship / Academic Honors Received</label>
              <input v-model="modalEdu.scholarship_academic_honors" placeholder="e.g. Magna Cum Laude, DOST Scholar" />
            </div>
            <div class="modal-actions">
              <button type="button" @click="activeModal = null" class="btn-cancel">Cancel</button>
              <button type="submit" class="btn-submit">{{ editingItemId ? 'Update Record' : 'Add Record' }}</button>
            </div>
          </form>
        </div>

        <!-- Eligibility Modal -->
        <div v-else-if="activeModal === 'eligibility'">
          <h3>{{ editingItemId ? 'Edit Civil Service Eligibility' : 'Add Civil Service Eligibility' }}</h3>
          <p class="modal-sub">CSC Form 212 Item 27 — Career Service, RA 1080, PRC Board / Bar</p>
          <form @submit.prevent="submitEligibility">
            <div class="field library-field">
              <label>⚡ Select from Eligibility Library (Auto-fill)</label>
              <select @change="onSelectEligibilityLibrary" class="library-dropdown">
                <option value="">-- Choose standard civil service eligibility --</option>
                <option v-for="item in librariesStore.eligibilities" :key="item.id" :value="item.id">
                  {{ item.eligibility_type }}
                </option>
              </select>
            </div>
            <div class="field">
              <label>Eligibility Type *</label>
              <input v-model="modalEligibility.eligibility_type" required placeholder="e.g. RA 1080 (Teacher's Board), Career Service Professional" />
            </div>
            <div class="field">
              <label>Rating (If Applicable)</label>
              <input v-model="modalEligibility.rating" placeholder="e.g. 88.60%" />
            </div>
            <div class="form-grid-2">
              <div class="field">
                <label>Date of Examination / Conferment</label>
                <input v-model="modalEligibility.examination_date" type="date" />
              </div>
              <div class="field">
                <label>Place of Examination / Conferment</label>
                <input v-model="modalEligibility.examination_place" placeholder="City / Regional Office" />
              </div>
            </div>
            <div class="form-grid-2">
              <div class="field">
                <label>License Number (if applicable)</label>
                <input v-model="modalEligibility.license_number" placeholder="e.g. 1234567" />
              </div>
              <div class="field">
                <label>Date of Validity</label>
                <input v-model="modalEligibility.license_validity_date" type="date" />
              </div>
            </div>
            <div class="modal-actions">
              <button type="button" @click="activeModal = null" class="btn-cancel">Cancel</button>
              <button type="submit" class="btn-submit">{{ editingItemId ? 'Update Eligibility' : 'Add Eligibility' }}</button>
            </div>
          </form>
        </div>

        <!-- Work Experience Modal -->
        <div v-else-if="activeModal === 'work'">
          <h3>{{ editingItemId ? 'Edit Work Experience' : 'Add Work Experience' }}</h3>
          <p class="modal-sub">CSC Form 212 Item 28 — Start from recent work. DO NOT ABBREVIATE.</p>
          <form @submit.prevent="submitWork">
            <div class="field library-field">
              <label>⚡ Select from Work Experience Library (Auto-fill)</label>
              <select @change="onSelectWorkLibrary" class="library-dropdown">
                <option value="">-- Choose standard teaching or school position --</option>
                <option v-for="item in librariesStore.workExperiences" :key="item.id" :value="item.id">
                  {{ item.position_title }} — {{ item.department_agency_company }} (SG {{ item.salary_grade }})
                </option>
              </select>
            </div>
            <div class="field">
              <label>Position Title * (Write in full)</label>
              <input v-model="modalWork.position_title" required placeholder="e.g. Master Teacher I, Secondary School Teacher II" />
            </div>
            <div class="field">
              <label>Department / Agency / Office / Company * (Write in full)</label>
              <input v-model="modalWork.department_agency_company" required placeholder="e.g. Department of Education - Division of City Schools" />
            </div>
            <div class="form-grid-2">
              <div class="field">
                <label>From Date</label>
                <input v-model="modalWork.from_date" type="date" />
              </div>
              <div class="field">
                <label>To Date</label>
                <input v-model="modalWork.to_date" type="date" :disabled="modalWork.to_present" />
                <label class="cb-inline mt-1">
                  <input type="checkbox" v-model="modalWork.to_present" />
                  <span>Currently working here (Present)</span>
                </label>
              </div>
            </div>
            <div class="form-grid-2">
              <div class="field">
                <label>Monthly Salary (in figures)</label>
                <input v-model="modalWork.monthly_salary" type="number" step="0.01" placeholder="e.g. 35097.00" />
              </div>
              <div class="field">
                <label>Salary / Pay Grade &amp; Step (format: 00-0)</label>
                <input v-model="modalWork.salary_grade" placeholder="e.g. 18-1, 13-2" />
              </div>
            </div>
            <div class="form-grid-2">
              <div class="field">
                <label>Status of Appointment</label>
                <select v-model="modalWork.appointment_status">
                  <option value="">Select Status</option>
                  <option value="Permanent">Permanent</option>
                  <option value="Temporary">Temporary</option>
                  <option value="Casual">Casual</option>
                  <option value="Contractual">Contractual</option>
                  <option value="Coterminous">Coterminous</option>
                  <option value="Job Order">Job Order</option>
                  <option value="Elected">Elected</option>
                </select>
              </div>
              <div class="field">
                <label>Government Service?</label>
                <select v-model="modalWork.is_government_service">
                  <option :value="true">Yes</option>
                  <option :value="false">No</option>
                </select>
              </div>
            </div>
            <div class="modal-actions">
              <button type="button" @click="activeModal = null" class="btn-cancel">Cancel</button>
              <button type="submit" class="btn-submit">{{ editingItemId ? 'Update Work Record' : 'Add Work Record' }}</button>
            </div>
          </form>
        </div>

        <!-- Learning & Development Modal -->
        <div v-else-if="activeModal === 'ld'">
          <h3>{{ editingItemId ? 'Edit L&D Intervention' : 'Add L&D Intervention' }}</h3>
          <p class="modal-sub">CSC Form 212 Item 29 — DO NOT ABBREVIATE sponsoring institutions.</p>
          <form @submit.prevent="submitLD">
            <div class="field library-field">
              <label>⚡ Select from Training / L&D Library (Auto-fill)</label>
              <select @change="onSelectTrainingLibrary" class="library-dropdown">
                <option value="">-- Choose standard DepEd training program --</option>
                <option v-for="item in librariesStore.trainings" :key="item.id" :value="item.id">
                  {{ item.training_title }} ({{ item.ld_type }} • {{ item.default_hours }} hrs)
                </option>
              </select>
            </div>
            <div class="field">
              <label>Title of Training / Seminar * (Write in full)</label>
              <input v-model="modalLD.training_title" required placeholder="e.g. Regional Training on the MATATAG Curriculum for Teachers" />
            </div>
            <div class="form-grid-2">
              <div class="field">
                <label>From Date</label>
                <input v-model="modalLD.from_date" type="date" />
              </div>
              <div class="field">
                <label>To Date</label>
                <input v-model="modalLD.to_date" type="date" />
              </div>
            </div>
            <div class="form-grid-2">
              <div class="field">
                <label>Number of Hours</label>
                <input v-model="modalLD.number_of_hours" type="number" min="1" placeholder="e.g. 40" />
              </div>
              <div class="field">
                <label>Type of L&amp;D Intervention</label>
                <select v-model="modalLD.ld_type">
                  <option value="Technical">Technical</option>
                  <option value="Managerial">Managerial</option>
                  <option value="Supervisory">Supervisory</option>
                  <option value="Foundational">Foundational</option>
                  <option value="Cross-Cutting">Cross-Cutting</option>
                </select>
              </div>
            </div>
            <div class="field">
              <label>Conducted / Sponsored By * (Write in full)</label>
              <input v-model="modalLD.conducted_sponsored_by" required placeholder="e.g. Department of Education Regional Office" />
            </div>
            <div class="modal-actions">
              <button type="button" @click="activeModal = null" class="btn-cancel">Cancel</button>
              <button type="submit" class="btn-submit">{{ editingItemId ? 'Update Training' : 'Add Training' }}</button>
            </div>
          </form>
        </div>

        <!-- Voluntary Work Modal -->
        <div v-else-if="activeModal === 'voluntary'">
          <h3>{{ editingItemId ? 'Edit Voluntary Work' : 'Add Voluntary Work' }}</h3>
          <p class="modal-sub">CSC Form 212 Item 30 — Civic, NGO, or Voluntary Organizations</p>
          <form @submit.prevent="submitVoluntary">
            <div class="field library-field">
              <label>⚡ Select from Voluntary Work Library (Auto-fill)</label>
              <select @change="onSelectVoluntaryLibrary" class="library-dropdown">
                <option value="">-- Choose standard organization / civic role --</option>
                <option v-for="item in librariesStore.voluntaryWorks" :key="item.id" :value="item.id">
                  {{ item.organization_name_address }} ({{ item.position_nature_of_work }})
                </option>
              </select>
            </div>
            <div class="field">
              <label>Name &amp; Address of Organization * (Write in full)</label>
              <input v-model="modalVoluntary.organization_name_address" required placeholder="e.g. Philippine Red Cross - City Chapter, Main St." />
            </div>
            <div class="form-grid-2">
              <div class="field">
                <label>From Date</label>
                <input v-model="modalVoluntary.from_date" type="date" />
              </div>
              <div class="field">
                <label>To Date</label>
                <input v-model="modalVoluntary.to_date" type="date" />
              </div>
            </div>
            <div class="form-grid-2">
              <div class="field">
                <label>Number of Hours</label>
                <input v-model="modalVoluntary.number_of_hours" type="number" min="1" placeholder="e.g. 50" />
              </div>
              <div class="field">
                <label>Position / Nature of Work</label>
                <input v-model="modalVoluntary.position_nature_of_work" placeholder="e.g. Volunteer Youth Leader / First Aid Responder" />
              </div>
            </div>
            <div class="modal-actions">
              <button type="button" @click="activeModal = null" class="btn-cancel">Cancel</button>
              <button type="submit" class="btn-submit">{{ editingItemId ? 'Update Voluntary Record' : 'Add Voluntary Record' }}</button>
            </div>
          </form>
        </div>

        <!-- References Modal -->
        <div v-else-if="activeModal === 'reference'">
          <h3>{{ editingItemId ? 'Edit Reference' : 'Add Character Reference' }}</h3>
          <p class="modal-sub">CSC Form 212 Item 41 — Persons not related by consanguinity or affinity</p>
          <form @submit.prevent="submitReference">
            <div class="field">
              <label>Full Name * (First Name, MI, Surname)</label>
              <input v-model="modalReference.name" required placeholder="e.g. Juan M. Santos" />
            </div>
            <div class="field">
              <label>Office / Residential Address</label>
              <input v-model="modalReference.office_residential_address" placeholder="e.g. DepEd Division Office, Rizal St., Quezon City" />
            </div>
            <div class="field">
              <label>Contact No. and/or Email Address</label>
              <input v-model="modalReference.contact_no_email" placeholder="e.g. 0917-123-4567 / jmsantos@deped.gov.ph" />
            </div>
            <div class="modal-actions">
              <button type="button" @click="activeModal = null" class="btn-cancel">Cancel</button>
              <button type="submit" class="btn-submit">{{ editingItemId ? 'Update Reference' : 'Add Reference' }}</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Hidden Photo File Input for Passport-size Digital Picture Affixing -->
    <input
      type="file"
      ref="photoInputRef"
      accept="image/*"
      @change="handlePhotoSelected"
      style="display: none;"
    />

    <!-- Hidden Signature File Input for E-Signature Upload -->
    <input
      type="file"
      ref="signatureInputRef"
      accept="image/*"
      @change="handleSignatureFileSelected"
      style="display: none;"
    />

    <!-- PDF Preview Modal -->
    <PdfPreviewModal
      :show="showPreviewModal"
      :teacherId="pds?.id"
      :teacherName="pds?.user?.full_name"
      @close="showPreviewModal = false"
    />

    <!-- Signature Pad Modal -->
    <SignaturePadModal
      :show="showSignatureModal"
      :teacherId="pds?.id"
      @close="showSignatureModal = false"
      @saved="handleSignatureCanvasSaved"
    />

    <!-- User Profile Modal -->
    <UserProfileModal
      :isOpen="showUserProfileModal"
      :targetUser="pds?.user"
      @close="showUserProfileModal = false"
      @saved="loadData"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, watch } from 'vue'
import { useRoute } from 'vue-router'
import { usePDSStore } from '@/stores/pds'
import { useAuthStore } from '@/stores/auth'
import { useLibrariesStore } from '@/stores/libraries'
import PdfPreviewModal from '@/components/PdfPreviewModal.vue'
import SignaturePadModal from '@/components/SignaturePadModal.vue'
import UserProfileModal from '@/components/UserProfileModal.vue'
import PhilippineAddressSelector from '@/components/PhilippineAddressSelector.vue'
import notify from '@/utils/notify'

const showUserProfileModal = ref(false)

const route = useRoute()
const pdsStore = usePDSStore()
const authStore = useAuthStore()
const librariesStore = useLibrariesStore()

const loading = ref(true)
const pds = ref(null)
const currentSection = ref(0)
const showPreviewModal = ref(false)
const photoInputRef = ref(null)
const isUploadingPhoto = ref(false)
const showSignatureModal = ref(false)
const signatureInputRef = ref(null)
const isUploadingSignature = ref(false)

// Section Wizard Tabs (Covering All CS Form 212 Sections & Item 42 Requirements)
const sections = [
  { num: 'I', title: 'Personal Info' },
  { num: 'II', title: 'Family & Children' },
  { num: 'III', title: 'Education' },
  { num: 'IV', title: 'Eligibility' },
  { num: 'V', title: 'Work Experience' },
  { num: 'VI', title: 'L&D / Training' },
  { num: 'VII', title: 'Voluntary Work' },
  { num: 'VIII', title: 'Other Info' },
  { num: 'IX', title: 'Questions 34–40' },
  { num: 'X', title: 'References & Item 42' },
  { num: 'XI', title: 'Declaration & Jurat' },
]

// Section Reactive State Forms
const formPersonal = reactive({})
const formFamily = reactive({})
const childrenList = ref([])
const formDecl = reactive({})
const otherInfoForm = reactive({
  special_skills_hobbies: [],
  non_academic_distinctions: [],
  organization_memberships: []
})
const govQuestionsForm = reactive({})

// Tag Input temporaries for Section VIII
const newSkill = ref('')
const newDistinction = ref('')
const newMembership = ref('')

// Modal CRUD state
const activeModal = ref(null)
const editingItemId = ref(null)
const modalEdu = reactive({})
const modalEligibility = reactive({})
const modalWork = reactive({})
const modalLD = reactive({})
const modalVoluntary = reactive({})
const modalReference = reactive({})

// Format Helper
const formatDate = (d) => {
  if (!d) return ''
  const parsed = new Date(d)
  return parsed.toLocaleDateString('en-PH', { year: 'numeric', month: 'short', day: 'numeric' })
}

// Data Loader
const loadData = async () => {
  loading.value = true
  try {
    librariesStore.fetchAllLibraries()
    let teacherId = route.params.id
    let data = null
    if (teacherId) {
      data = await pdsStore.fetchPDSSummary(teacherId)
    } else {
      data = await pdsStore.fetchMyProfile()
    }
    pds.value = data

    // Populate Section I
    if (data.personal_info) {
      Object.assign(formPersonal, data.personal_info)
    }

    // Populate Section II
    if (data.family_background) {
      Object.assign(formFamily, data.family_background)
      childrenList.value = (data.family_background.children || []).map(c => ({ ...c }))
    }

    // Populate Section VIII
    if (data.other_information) {
      otherInfoForm.special_skills_hobbies = [...(data.other_information.special_skills_hobbies || [])]
      otherInfoForm.non_academic_distinctions = [...(data.other_information.non_academic_distinctions || [])]
      otherInfoForm.organization_memberships = [...(data.other_information.organization_memberships || [])]
    }

    // Populate Questions 34-40
    if (data.government_questions) {
      Object.assign(govQuestionsForm, data.government_questions)
    }

    // Populate Declaration
    if (data.pds_declaration) {
      Object.assign(formDecl, data.pds_declaration)
    }
  } catch (err) {
    console.error('Failed to load PDS dossier:', err)
  } finally {
    loading.value = false
  }
}

// Section I: Save Personal Info
const savePersonal = async () => {
  await pdsStore.savePersonalInfo(pds.value.id, formPersonal)
  notify.success('Personal Information (Section I) saved successfully!')
}

const copyResidentialToPermanent = () => {
  formPersonal.perm_house_block_lot = formPersonal.res_house_block_lot || ''
  formPersonal.perm_street = formPersonal.res_street || ''
  formPersonal.perm_subdivision_village = formPersonal.res_subdivision_village || ''
  formPersonal.perm_province = formPersonal.res_province || ''
  formPersonal.perm_city_municipality = formPersonal.res_city_municipality || ''
  formPersonal.perm_barangay = formPersonal.res_barangay || ''
  formPersonal.perm_zip_code = formPersonal.res_zip_code || ''
  notify.success('Copied Residential Address to Permanent Address.')
}

// Library Select Handlers for Modals
const onSelectEligibilityLibrary = (e) => {
  const libId = e.target.value
  if (!libId) return
  const item = librariesStore.eligibilities.find(x => x.id == libId)
  if (item) {
    modalEligibility.eligibility_type = item.eligibility_type
    if (item.exam_place_hint) {
      modalEligibility.examination_place = item.exam_place_hint
    }
  }
}

const onSelectWorkLibrary = (e) => {
  const libId = e.target.value
  if (!libId) return
  const item = librariesStore.workExperiences.find(x => x.id == libId)
  if (item) {
    modalWork.position_title = item.position_title
    modalWork.department_agency_company = item.department_agency_company
    if (item.salary_grade) modalWork.salary_grade = item.salary_grade
    if (item.appointment_status) modalWork.appointment_status = item.appointment_status
    if (item.is_government_service !== undefined) modalWork.is_government_service = item.is_government_service
  }
}

const onSelectTrainingLibrary = (e) => {
  const libId = e.target.value
  if (!libId) return
  const item = librariesStore.trainings.find(x => x.id == libId)
  if (item) {
    modalLD.training_title = item.training_title
    if (item.ld_type) modalLD.ld_type = item.ld_type
    if (item.default_hours) modalLD.number_of_hours = item.default_hours
    if (item.conducted_sponsored_by) modalLD.conducted_sponsored_by = item.conducted_sponsored_by
  }
}

const onSelectVoluntaryLibrary = (e) => {
  const libId = e.target.value
  if (!libId) return
  const item = librariesStore.voluntaryWorks.find(x => x.id == libId)
  if (item) {
    modalVoluntary.organization_name_address = item.organization_name_address
    if (item.position_nature_of_work) modalVoluntary.position_nature_of_work = item.position_nature_of_work
    if (item.default_hours) modalVoluntary.number_of_hours = item.default_hours
  }
}

// Section II: Save Family & Children
const addChildRow = () => {
  childrenList.value.push({ name: '', date_of_birth: null })
}

const removeChildRow = (idx) => {
  childrenList.value.splice(idx, 1)
}

const saveFamily = async () => {
  const payload = {
    ...formFamily,
    children: childrenList.value.filter(c => c.name && c.name.trim())
  }
  await pdsStore.saveFamilyBackground(pds.value.id, payload)
  notify.success('Family Background & Children (Section II) saved successfully!')
}

// Section VIII: Tags Management
const addTag = (category) => {
  if (category === 'skills' && newSkill.value.trim()) {
    otherInfoForm.special_skills_hobbies.push(newSkill.value.trim())
    newSkill.value = ''
  } else if (category === 'distinctions' && newDistinction.value.trim()) {
    otherInfoForm.non_academic_distinctions.push(newDistinction.value.trim())
    newDistinction.value = ''
  } else if (category === 'memberships' && newMembership.value.trim()) {
    otherInfoForm.organization_memberships.push(newMembership.value.trim())
    newMembership.value = ''
  }
}

const removeTag = (category, idx) => {
  if (category === 'skills') otherInfoForm.special_skills_hobbies.splice(idx, 1)
  else if (category === 'distinctions') otherInfoForm.non_academic_distinctions.splice(idx, 1)
  else if (category === 'memberships') otherInfoForm.organization_memberships.splice(idx, 1)
}

const saveOtherInformation = async () => {
  await pdsStore.saveOtherInfo(pds.value.id, otherInfoForm)
  notify.success('Other Information (Section VIII) saved successfully!')
}

// Section IX: Government Questions
const saveGovernmentQuestions = async () => {
  await pdsStore.saveGovQuestions(pds.value.id, govQuestionsForm)
  notify.success('Government Questions (Items 34–40) saved successfully!')
}

// Photo Upload & Affixing (Item 42)
const triggerPhotoUpload = () => {
  if (photoInputRef.value) {
    photoInputRef.value.click()
  }
}

const handlePhotoSelected = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  isUploadingPhoto.value = true
  try {
    const res = await pdsStore.uploadPhoto(pds.value.id, file)
    if (res.photo_url) {
      pds.value.photo_url = res.photo_url
    } else {
      await loadData()
    }
    notify.success('Passport-sized digital picture (4.5 cm x 3.5 cm) affixed successfully!')
  } catch (err) {
    console.error('Photo upload failed:', err)
    notify.error('Failed to upload picture. Please verify the file is a valid image.')
  } finally {
    isUploadingPhoto.value = false
    if (event.target) event.target.value = ''
  }
}

const removeAffixedPhoto = async () => {
  const confirmed = await notify.confirm({
    title: 'Remove Photo?',
    text: 'Are you sure you want to remove the affixed passport photo?',
    confirmButtonText: 'Yes, Remove Photo'
  })
  if (!confirmed) return
  try {
    await pdsStore.removePhoto(pds.value.id)
    pds.value.photo_url = null
    notify.success('Affixed photo removed.')
  } catch (err) {
    console.error('Failed to remove photo:', err)
    notify.error('Failed to remove photo.')
  }
}

// E-Signature Handlers (Item 42)
const triggerSignatureUpload = () => {
  if (signatureInputRef.value) {
    signatureInputRef.value.click()
  }
}

const handleSignatureFileSelected = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  isUploadingSignature.value = true
  try {
    const res = await pdsStore.uploadSignature(pds.value.id, file)
    if (res.signature_url) {
      pds.value.signature_url = res.signature_url
    } else {
      await loadData()
    }
    notify.success('Electronic signature attached successfully!')
  } catch (err) {
    console.error('Signature upload failed:', err)
    notify.error('Failed to upload signature. Please ensure it is a valid image file.')
  } finally {
    isUploadingSignature.value = false
    if (event.target) event.target.value = ''
  }
}

const handleSignatureCanvasSaved = async (blob) => {
  isUploadingSignature.value = true
  try {
    const res = await pdsStore.uploadSignature(pds.value.id, blob)
    if (res.signature_url) {
      pds.value.signature_url = res.signature_url
    } else {
      await loadData()
    }
    notify.success('Hand-drawn electronic signature attached successfully!')
  } catch (err) {
    console.error('Signature save failed:', err)
    notify.error('Failed to save drawn signature.')
  } finally {
    isUploadingSignature.value = false
  }
}

const removeAttachedSignature = async () => {
  const confirmed = await notify.confirm({
    title: 'Remove Signature?',
    text: 'Are you sure you want to remove the attached electronic signature?',
    confirmButtonText: 'Yes, Remove Signature'
  })
  if (!confirmed) return
  try {
    await pdsStore.removeSignature(pds.value.id)
    pds.value.signature_url = null
    notify.success('Attached signature removed.')
  } catch (err) {
    console.error('Failed to remove signature:', err)
    notify.error('Failed to remove signature.')
  }
}

// Section X & XI: Declaration
const saveDeclaration = async () => {
  await pdsStore.saveDeclaration(pds.value.id, formDecl)
  notify.success('Item 42 Declaration, Government ID, Signature & Oath saved successfully!')
}

// Modal Handlers
const openCreateModal = (type) => {
  editingItemId.value = null
  activeModal.value = type
  if (type === 'education') {
    Object.assign(modalEdu, { level: 'College', school_name: '', degree_course: '', from_year: '', to_year: '', highest_level_units_earned: '', year_graduated: '', scholarship_academic_honors: '' })
  } else if (type === 'eligibility') {
    Object.assign(modalEligibility, { eligibility_type: '', rating: '', examination_date: null, examination_place: '', license_number: '', license_validity_date: null })
  } else if (type === 'work') {
    Object.assign(modalWork, { position_title: '', department_agency_company: '', from_date: null, to_date: null, to_present: false, monthly_salary: null, salary_grade: '', appointment_status: 'Permanent', is_government_service: true })
  } else if (type === 'ld') {
    Object.assign(modalLD, { training_title: '', from_date: null, to_date: null, number_of_hours: 8, ld_type: 'Technical', conducted_sponsored_by: '' })
  } else if (type === 'voluntary') {
    Object.assign(modalVoluntary, { organization_name_address: '', from_date: null, to_date: null, number_of_hours: 8, position_nature_of_work: '' })
  } else if (type === 'reference') {
    Object.assign(modalReference, { name: '', office_residential_address: '', contact_no_email: '' })
  }
}

const openEditModal = (type, item) => {
  editingItemId.value = item.id
  activeModal.value = type
  if (type === 'education') Object.assign(modalEdu, item)
  else if (type === 'eligibility') Object.assign(modalEligibility, item)
  else if (type === 'work') Object.assign(modalWork, item)
  else if (type === 'ld') Object.assign(modalLD, item)
  else if (type === 'voluntary') Object.assign(modalVoluntary, item)
  else if (type === 'reference') Object.assign(modalReference, item)
}

// Submissions
const submitEdu = async () => {
  if (editingItemId.value) {
    await pdsStore.updateEducation(pds.value.id, editingItemId.value, modalEdu)
  } else {
    await pdsStore.addEducation(pds.value.id, modalEdu)
  }
  activeModal.value = null
}

const deleteEdu = async (id) => {
  if (confirm('Delete this educational background entry?')) {
    await pdsStore.deleteEducation(pds.value.id, id)
  }
}

const submitEligibility = async () => {
  if (editingItemId.value) {
    await pdsStore.updateEligibility(pds.value.id, editingItemId.value, modalEligibility)
  } else {
    await pdsStore.addEligibility(pds.value.id, modalEligibility)
  }
  activeModal.value = null
}

const deleteCse = async (id) => {
  if (confirm('Delete this civil service eligibility record?')) {
    await pdsStore.deleteEligibility(pds.value.id, id)
  }
}

const submitWork = async () => {
  if (editingItemId.value) {
    await pdsStore.updateWorkExperience(pds.value.id, editingItemId.value, modalWork)
  } else {
    await pdsStore.addWorkExperience(pds.value.id, modalWork)
  }
  activeModal.value = null
}

const deleteWe = async (id) => {
  if (confirm('Delete this work experience record?')) {
    await pdsStore.deleteWorkExperience(pds.value.id, id)
  }
}

const submitLD = async () => {
  if (editingItemId.value) {
    await pdsStore.updateLD(pds.value.id, editingItemId.value, modalLD)
  } else {
    await pdsStore.addLD(pds.value.id, modalLD)
  }
  activeModal.value = null
}

const deleteLd = async (id) => {
  if (confirm('Delete this training record?')) {
    await pdsStore.deleteLD(pds.value.id, id)
  }
}

const submitVoluntary = async () => {
  if (editingItemId.value) {
    await pdsStore.updateVoluntaryWork(pds.value.id, editingItemId.value, modalVoluntary)
  } else {
    await pdsStore.addVoluntaryWork(pds.value.id, modalVoluntary)
  }
  activeModal.value = null
}

const deleteVw = async (id) => {
  if (confirm('Delete this voluntary work record?')) {
    await pdsStore.deleteVoluntaryWork(pds.value.id, id)
  }
}

const submitReference = async () => {
  if (editingItemId.value) {
    await pdsStore.updateReference(pds.value.id, editingItemId.value, modalReference)
  } else {
    await pdsStore.addReference(pds.value.id, modalReference)
  }
  activeModal.value = null
}

const deleteRef = async (id) => {
  if (confirm('Delete this reference?')) {
    await pdsStore.deleteReference(pds.value.id, id)
  }
}

// PDF Download
const downloadPDF = () => {
  pdsStore.exportPDF(pds.value.id, pds.value.user?.full_name)
}

// Excel Download
const isDownloadingExcel = ref(false)
const downloadExcel = async () => {
  if (!pds.value?.id) return
  isDownloadingExcel.value = true
  try {
    await pdsStore.exportExcel(pds.value.id, pds.value.user?.full_name)
  } finally {
    isDownloadingExcel.value = false
  }
}

watch(() => route.params.id, () => {
  loadData()
})

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.pds-wizard-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Banner */
.teacher-banner {
  padding: 1.5rem 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.banner-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--bg-surface-elevated);
  color: var(--accent-gold);
  border: 2px solid var(--accent-gold);
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.banner-info {
  flex: 1;
}

.role-desc {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

.banner-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-preview-banner {
  background: var(--accent-gold-subtle);
  color: var(--accent-gold);
  border: 1px solid rgba(245, 158, 11, 0.4);
  padding: 0.65rem 1.15rem;
  border-radius: var(--radius-sm);
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  transition: all 0.2s ease;
}

.btn-preview-banner:hover {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
}

.btn-export {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  font-weight: 700;
  padding: 0.65rem 1.25rem;
  border-radius: var(--radius-sm);
}

.btn-export:hover {
  background: var(--accent-gold-hover);
}

.btn-export-excel {
  background: linear-gradient(135deg, #10b981, #059669);
  color: #ffffff;
  font-weight: 700;
  padding: 0.65rem 1.25rem;
  border-radius: var(--radius-sm);
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
  transition: all 0.2s ease;
}

.btn-export-excel:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669, #047857);
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(16, 185, 129, 0.4);
}

.btn-export-excel:disabled {
  opacity: 0.7;
  cursor: wait;
}

.btn-account-profile {
  background: rgba(254, 203, 144, 0.15);
  border: 1px solid rgba(254, 203, 144, 0.35);
  color: #fecb90;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.btn-account-profile:hover {
  background: rgba(254, 203, 144, 0.28);
  border-color: #fecb90;
  transform: translateY(-1px);
}

/* Wizard Nav */
.wizard-nav {
  display: flex;
  overflow-x: auto;
  padding: 0.5rem;
  gap: 0.5rem;
  scrollbar-width: thin;
}

.nav-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1rem;
  background: transparent;
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  white-space: nowrap;
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

/* Section Content */
.section-content {
  padding: 2rem;
}

.section-title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 1rem;
}

.section-sub {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
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
  font-size: 0.95rem;
  color: var(--accent-gold);
  margin: 1.5rem 0 0.85rem;
  border-bottom: 1px dashed rgba(245, 158, 11, 0.25);
  padding-bottom: 0.4rem;
}

/* Grids */
.form-grid-1 { display: grid; grid-template-columns: 1fr; gap: 1rem; margin-bottom: 1rem; }
.form-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.form-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.form-grid-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem; }

@media (max-width: 768px) {
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

.field-help {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
}

/* Citizenship Box */
.citizenship-box {
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  padding: 1rem;
  border-radius: var(--radius-sm);
  margin-bottom: 1.5rem;
}

.checkbox-row {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.cb-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  cursor: pointer;
}

.cb-label input[type="checkbox"],
.cb-inline input[type="checkbox"] {
  width: auto;
}

.cb-inline {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
  cursor: pointer;
}

.dual-options {
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-color);
}

/* Address Header */
.address-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
}

.btn-copy-address {
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 0.78rem;
  padding: 0.3rem 0.65rem;
  border-radius: var(--radius-sm);
}

.btn-copy-address:hover {
  color: var(--accent-gold);
  border-color: var(--accent-gold);
}

/* Sub-Tables */
.sub-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.sub-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1.5rem;
}

.sub-table th {
  padding: 0.75rem 1rem;
  background: rgba(11, 19, 41, 0.4);
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-color);
  text-align: left;
}

.sub-table td {
  padding: 0.85rem 1rem;
  font-size: 0.85rem;
  border-bottom: 1px solid var(--border-color);
  vertical-align: middle;
}

.action-cell {
  display: flex;
  gap: 0.4rem;
}

.btn-add {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  font-weight: 700;
  padding: 0.45rem 1rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
}

.btn-edit {
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  font-size: 0.75rem;
  padding: 0.25rem 0.55rem;
  border-radius: 4px;
}

.btn-edit:hover {
  border-color: var(--accent-gold);
  color: var(--accent-gold);
}

.btn-del {
  background: rgba(244, 63, 94, 0.15);
  color: #fda4af;
  border: 1px solid rgba(244, 63, 94, 0.3);
  font-size: 0.75rem;
  padding: 0.25rem 0.55rem;
  border-radius: 4px;
}

.btn-del:hover {
  background: var(--accent-rose);
  color: white;
}

.type-pill {
  font-size: 0.72rem;
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
  color: var(--accent-gold);
}

.no-records {
  text-align: center;
  color: var(--text-muted);
  padding: 2rem !important;
}

/* Other Info Cards & Tags */
.other-info-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
}

.other-info-card h4 {
  font-size: 0.95rem;
  color: var(--accent-gold);
  margin-bottom: 0.25rem;
}

.add-tag-row {
  display: flex;
  gap: 0.4rem;
  margin-bottom: 1rem;
}

.btn-tag-add {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  font-weight: 800;
  padding: 0 0.85rem;
  font-size: 1.1rem;
  border-radius: var(--radius-sm);
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  min-height: 80px;
  background: rgba(11, 19, 41, 0.4);
  padding: 0.6rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
}

.info-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 0.2rem 0.55rem;
  border-radius: 12px;
  font-size: 0.8rem;
}

.tag-remove {
  background: transparent;
  color: var(--text-muted);
  font-size: 1rem;
  cursor: pointer;
}

.tag-remove:hover {
  color: var(--accent-rose);
}

.empty-tag-text {
  color: var(--text-muted);
  font-size: 0.8rem;
  margin: auto;
}

/* Questions 34-40 */
.question-card {
  padding: 1.25rem;
  margin-bottom: 1.25rem;
}

.question-text {
  font-size: 0.88rem;
  color: var(--text-primary);
  margin-bottom: 0.85rem;
  line-height: 1.5;
}

.question-item label {
  font-size: 0.82rem;
  color: var(--text-secondary);
}

.radio-options {
  display: flex;
  gap: 1.5rem;
  margin-top: 0.35rem;
}

.radio-options label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  cursor: pointer;
  color: var(--text-primary);
  font-weight: 600;
}

.radio-options input[type="radio"] {
  width: auto;
}

/* Sheet C4 Completion Banner */
.c4-completion-banner {
  background: linear-gradient(90deg, rgba(245, 158, 11, 0.15) 0%, rgba(245, 158, 11, 0.03) 100%);
  border-left: 4px solid var(--accent-gold);
  border-radius: var(--radius-sm);
  padding: 1rem 1.25rem;
  margin: 2.5rem 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.c4-completion-banner h4 {
  color: var(--accent-gold);
  font-size: 0.95rem;
  font-weight: 700;
  margin-bottom: 0.2rem;
}

/* Item 42 Container */
.item42-container {
  margin-top: 1rem;
}

.declaration-oath-card {
  background: rgba(245, 158, 11, 0.06);
  border: 1.5px solid rgba(245, 158, 11, 0.3);
  padding: 1.25rem 1.5rem;
  border-radius: var(--radius-sm);
  margin-bottom: 1.5rem;
}

.oath-title-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.65rem;
}

.oath-badge {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  font-weight: 800;
  font-size: 0.7rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.oath-heading {
  color: var(--accent-gold);
  font-size: 0.95rem;
  font-weight: 800;
  letter-spacing: 0.5px;
}

.oath-full-text {
  font-size: 0.84rem;
  color: var(--text-primary);
  line-height: 1.65;
  text-align: justify;
}

/* 3-Column Execution Grid */
.item42-execution-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1.15fr;
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

@media (max-width: 1100px) {
  .item42-execution-grid {
    grid-template-columns: 1fr;
  }
}

.execution-col {
  padding: 1.25rem;
  border-radius: var(--radius-sm);
  display: flex;
  flex-direction: column;
}

.col-header {
  margin-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 0.5rem;
}

.col-header h5 {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--accent-gold);
}

.col-sub {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.15rem;
}

/* Signature Card */
.badge-e-sig {
  display: inline-block;
  font-size: 0.7rem;
  font-style: italic;
  color: var(--text-muted);
  margin-top: 0.2rem;
}

.signature-box-container {
  margin-top: 0.25rem;
}

.sign-inside-box {
  border: 2px dashed rgba(245, 158, 11, 0.45);
  background: rgba(0, 0, 0, 0.35);
  min-height: 110px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border-radius: 6px;
  padding: 1rem 0.75rem;
  text-align: center;
}

.signature-line {
  padding-bottom: 0.4rem;
  width: 90%;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}

.signature-script {
  font-family: 'Brush Script MT', 'Dancing Script', 'Caveat', cursive, Georgia, serif;
  font-size: 1.85rem;
  color: var(--accent-gold);
  text-shadow: 0 0 12px rgba(245, 158, 11, 0.35);
  letter-spacing: 0.5px;
}

.e-cert-tag {
  font-size: 0.72rem;
  color: #34d399;
  font-weight: 600;
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.signature-img-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 0.25rem;
}

.attached-sig-img {
  max-height: 75px;
  max-width: 90%;
  object-fit: contain;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.4));
}

.sig-affiant-caption {
  font-size: 0.72rem;
  color: var(--text-secondary);
  font-weight: 600;
  margin-top: 0.25rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 0.2rem;
  width: 80%;
  text-align: center;
}

.sign-box-caption {
  text-align: center;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-secondary);
  margin-top: 0.5rem;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.sig-action-buttons {
  display: flex;
  gap: 0.35rem;
  margin-top: 0.65rem;
  width: 100%;
}

.btn-sig-action {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.35rem 0.6rem;
  border-radius: 4px;
  transition: all 0.2s;
  cursor: pointer;
}

.btn-draw-sig {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  flex: 1;
}

.btn-draw-sig:hover {
  background: var(--accent-gold-hover);
}

.btn-upload-sig {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-primary);
  border: 1px solid rgba(255, 255, 255, 0.15);
  flex: 1;
}

.btn-upload-sig:hover {
  background: rgba(255, 255, 255, 0.15);
}

.btn-remove-sig {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.4);
  padding: 0.35rem 0.6rem;
}

.btn-remove-sig:hover {
  background: rgba(239, 68, 68, 0.35);
}

.signature-legal-note {
  font-size: 0.72rem;
  color: var(--text-muted);
  line-height: 1.4;
  margin-top: 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  padding: 0.5rem;
  border-radius: 4px;
}

/* Passport Photo & Thumbmark */
.photo-thumb-dual {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  justify-content: center;
}

.passport-photo-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.passport-photo-frame {
  width: 135px;
  height: 174px; /* Strict 3.5cm x 4.5cm ratio */
  border: 2px solid var(--accent-gold);
  border-radius: 6px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.passport-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.passport-placeholder {
  text-align: center;
  padding: 0.5rem 0.3rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
}

.photo-icon {
  font-size: 1.5rem;
}

.passport-placeholder strong {
  font-size: 0.85rem;
  color: var(--text-primary);
}

.photo-dims {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--accent-gold);
}

.photo-note {
  font-size: 0.65rem;
  color: var(--text-muted);
  line-height: 1.2;
}

.photo-actions {
  display: flex;
  gap: 0.35rem;
  margin-top: 0.5rem;
  width: 100%;
}

.btn-photo-upload {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  font-weight: 700;
  font-size: 0.75rem;
  padding: 0.4rem 0.6rem;
  border-radius: 4px;
  flex: 1;
  transition: all 0.2s;
}

.btn-photo-upload:hover {
  background: var(--accent-gold-hover);
}

.btn-photo-remove {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.4);
  font-weight: 700;
  padding: 0.4rem 0.55rem;
  border-radius: 4px;
}

.thumbmark-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.thumbmark-frame {
  width: 125px;
  height: 135px;
  border: 2px dashed rgba(255, 255, 255, 0.25);
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.25);
  padding: 0.5rem;
  text-align: center;
  transition: all 0.3s;
}

.thumbmark-frame.affixed {
  border-color: #38bdf8;
  background: rgba(56, 189, 248, 0.1);
}

.thumb-icon {
  font-size: 1.6rem;
}

.thumb-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-top: 0.25rem;
}

.thumb-status {
  font-size: 0.65rem;
  color: var(--text-muted);
  margin-top: 0.2rem;
}

.cb-thumbmark {
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.72rem;
  color: var(--text-secondary);
  cursor: pointer;
}

.photo-disclaimer {
  font-size: 0.68rem;
  font-style: italic;
  color: var(--text-muted);
  margin-top: 0.75rem;
  text-align: center;
  line-height: 1.3;
}

/* Jurat / Person Administering Oath */
.jurat-card {
  padding: 1.5rem;
  border-radius: var(--radius-sm);
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
}

.jurat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.jurat-header h5 {
  font-size: 0.92rem;
  color: var(--accent-gold);
  font-weight: 700;
}

.jurat-sub {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-style: italic;
}

.jurat-statement {
  font-size: 0.84rem;
  font-style: italic;
  color: var(--text-primary);
  line-height: 1.6;
  background: rgba(0, 0, 0, 0.25);
  padding: 0.85rem 1.15rem;
  border-left: 3px solid var(--accent-gold);
  border-radius: 4px;
  margin-bottom: 1.25rem;
}

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.btn-save {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  font-weight: 700;
  padding: 0.75rem 1.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
}

.btn-save:hover {
  background: var(--accent-gold-hover);
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(4, 9, 23, 0.8);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1.5rem;
}

.modal-card {
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  background: #111a33;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-md);
  padding: 2rem;
}

.modal-card h3 {
  margin-bottom: 0.25rem;
}

.modal-sub {
  font-size: 0.82rem;
  color: var(--text-muted);
  margin-bottom: 1.25rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.btn-cancel {
  background: var(--bg-surface-elevated);
  color: var(--text-secondary);
  padding: 0.55rem 1.25rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
}

.btn-submit {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  font-weight: 700;
  padding: 0.55rem 1.25rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
}

/* Loading */
.loading-state {
  text-align: center;
  padding: 5rem 1rem;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(245, 158, 11, 0.15);
  border-top-color: var(--accent-gold);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1.25rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.mt-1 { margin-top: 0.25rem; }
.mt-2 { margin-top: 0.5rem; }
.mt-3 { margin-top: 0.75rem; }

/* Library Dropdown Pickers in Modals */
.library-field {
  background: rgba(14, 165, 233, 0.08) !important;
  border: 1px solid rgba(14, 165, 233, 0.25) !important;
  border-radius: 8px !important;
  padding: 0.75rem 0.85rem !important;
  margin-bottom: 1rem !important;
}

.library-field label {
  color: #38bdf8 !important;
  font-weight: 700 !important;
  font-size: 0.8rem !important;
  margin-bottom: 0.4rem !important;
  display: block;
}

.library-dropdown {
  width: 100%;
  padding: 0.55rem 0.75rem;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(56, 189, 248, 0.4);
  border-radius: 6px;
  color: #f8fafc;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.library-dropdown:focus {
  outline: none;
  border-color: #38bdf8;
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25);
}
</style>
