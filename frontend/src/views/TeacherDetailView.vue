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
          <span>ID: {{ pds.employee_id || 'N/A' }}</span>
        </p>
      </div>
      <div class="banner-actions">
        <button @click="downloadPDF" class="btn-export">
          📄 Export CS Form 212 (PDF)
        </button>
      </div>
    </div>

    <!-- Multi-section Wizard Tabs -->
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
      <!-- Section I: Personal Information -->
      <div v-if="currentSection === 0" class="form-section">
        <h3>I. Personal Information (Items 1–21)</h3>
        <p class="section-sub">Official legal identity records</p>

        <form @submit.prevent="savePersonal">
          <div class="form-grid-3">
            <div class="field">
              <label>1. Surname</label>
              <input v-model="formPersonal.surname" required />
            </div>
            <div class="field">
              <label>2. First Name</label>
              <input v-model="formPersonal.first_name" required />
            </div>
            <div class="field">
              <label>Middle Name</label>
              <input v-model="formPersonal.middle_name" />
            </div>
          </div>

          <div class="form-grid-4">
            <div class="field">
              <label>Name Extension</label>
              <input v-model="formPersonal.name_extension" placeholder="e.g. JR., III" />
            </div>
            <div class="field">
              <label>3. Date of Birth</label>
              <input v-model="formPersonal.date_of_birth" type="date" />
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

          <div class="form-grid-3">
            <div class="field">
              <label>4. Place of Birth</label>
              <input v-model="formPersonal.place_of_birth" />
            </div>
            <div class="field">
              <label>7. Height (m)</label>
              <input v-model="formPersonal.height_m" type="number" step="0.01" placeholder="e.g. 1.65" />
            </div>
            <div class="field">
              <label>8. Weight (kg)</label>
              <input v-model="formPersonal.weight_kg" type="number" step="0.1" placeholder="e.g. 62.5" />
            </div>
          </div>

          <h4 class="sub-heading">Government Identification Numbers</h4>
          <div class="form-grid-3">
            <div class="field">
              <label>10. UMID ID NO.</label>
              <input v-model="formPersonal.umid_id_no" />
            </div>
            <div class="field">
              <label>11. PAG-IBIG ID NO.</label>
              <input v-model="formPersonal.pag_ibig_id_no" />
            </div>
            <div class="field">
              <label>12. PHILHEALTH NO.</label>
              <input v-model="formPersonal.philhealth_no" />
            </div>
          </div>

          <div class="form-grid-3">
            <div class="field">
              <label>13. PhilSys Card (PCN)</label>
              <input v-model="formPersonal.philsys_pcn" />
            </div>
            <div class="field">
              <label>14. TIN NO.</label>
              <input v-model="formPersonal.tin_no" />
            </div>
            <div class="field">
              <label>15. Agency Employee No.</label>
              <input v-model="formPersonal.agency_employee_no" />
            </div>
          </div>

          <h4 class="sub-heading">Residential & Permanent Address</h4>
          <div class="form-grid-2">
            <div class="field">
              <label>17. Residential Address (Full Line)</label>
              <input v-model="formPersonal.res_city_municipality" placeholder="City / Municipality" />
            </div>
            <div class="field">
              <label>Province</label>
              <input v-model="formPersonal.res_province" />
            </div>
          </div>

          <div class="form-grid-3">
            <div class="field">
              <label>19. Telephone No.</label>
              <input v-model="formPersonal.telephone_no" />
            </div>
            <div class="field">
              <label>20. Mobile No.</label>
              <input v-model="formPersonal.mobile_no" />
            </div>
            <div class="field">
              <label>21. Email Address</label>
              <input v-model="formPersonal.email_address" type="email" />
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-save" :disabled="pdsStore.isSaving">
              {{ pdsStore.isSaving ? 'Saving...' : 'Save Personal Info' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Section II: Family Background -->
      <div v-else-if="currentSection === 1" class="form-section">
        <h3>II. Family Background (Items 22–25)</h3>
        <p class="section-sub">Spouse, Parents, and Children</p>

        <form @submit.prevent="saveFamily">
          <h4 class="sub-heading">Spouse Information (Item 22)</h4>
          <div class="form-grid-3">
            <div class="field">
              <label>Spouse Surname</label>
              <input v-model="formFamily.spouse_surname" />
            </div>
            <div class="field">
              <label>First Name</label>
              <input v-model="formFamily.spouse_first_name" />
            </div>
            <div class="field">
              <label>Middle Name</label>
              <input v-model="formFamily.spouse_middle_name" />
            </div>
          </div>

          <div class="form-grid-2">
            <div class="field">
              <label>Occupation</label>
              <input v-model="formFamily.spouse_occupation" />
            </div>
            <div class="field">
              <label>Employer / Business</label>
              <input v-model="formFamily.spouse_employer_business_name" />
            </div>
          </div>

          <h4 class="sub-heading">Parents (Items 24–25)</h4>
          <div class="form-grid-3">
            <div class="field">
              <label>Father's Surname</label>
              <input v-model="formFamily.father_surname" />
            </div>
            <div class="field">
              <label>First Name</label>
              <input v-model="formFamily.father_first_name" />
            </div>
            <div class="field">
              <label>Middle Name</label>
              <input v-model="formFamily.father_middle_name" />
            </div>
          </div>

          <div class="form-grid-3">
            <div class="field">
              <label>Mother's Maiden Surname</label>
              <input v-model="formFamily.mother_surname" />
            </div>
            <div class="field">
              <label>First Name</label>
              <input v-model="formFamily.mother_first_name" />
            </div>
            <div class="field">
              <label>Middle Name</label>
              <input v-model="formFamily.mother_middle_name" />
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-save" :disabled="pdsStore.isSaving">
              Save Family Background
            </button>
          </div>
        </form>
      </div>

      <!-- Section III: Educational Background -->
      <div v-else-if="currentSection === 2" class="form-section">
        <div class="sub-header">
          <div>
            <h3>III. Educational Background (Item 26)</h3>
            <p class="section-sub">Elementary, Secondary, College, and Graduate Studies</p>
          </div>
          <button @click="openModal('education')" class="btn-add">+ Add Record</button>
        </div>

        <table class="sub-table">
          <thead>
            <tr>
              <th>Level</th>
              <th>School Name</th>
              <th>Degree / Course</th>
              <th>Period</th>
              <th>Year Graduated</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="edu in pds.educational_backgrounds" :key="edu.id">
              <td><strong>{{ edu.level }}</strong></td>
              <td>{{ edu.school_name }}</td>
              <td>{{ edu.degree_course || '—' }}</td>
              <td>{{ edu.from_year }} - {{ edu.to_year }}</td>
              <td>{{ edu.year_graduated || '—' }}</td>
              <td>
                <button @click="deleteEdu(edu.id)" class="btn-del">Delete</button>
              </td>
            </tr>
            <tr v-if="!pds.educational_backgrounds?.length">
              <td colspan="6" class="no-records">No educational records yet.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Section IV: Civil Service Eligibility -->
      <div v-else-if="currentSection === 3" class="form-section">
        <div class="sub-header">
          <div>
            <h3>IV. Civil Service Eligibility (Item 27)</h3>
            <p class="section-sub">RA 1080 (Board/Bar), Career Service, PRC Licensure</p>
          </div>
          <button @click="openModal('eligibility')" class="btn-add">+ Add Eligibility</button>
        </div>

        <table class="sub-table">
          <thead>
            <tr>
              <th>Eligibility Type</th>
              <th>Rating</th>
              <th>Exam Date</th>
              <th>Place</th>
              <th>License No.</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cse in pds.civil_service_eligibilities" :key="cse.id">
              <td><strong>{{ cse.eligibility_type }}</strong></td>
              <td>{{ cse.rating || 'N/A' }}</td>
              <td>{{ cse.examination_date || '—' }}</td>
              <td>{{ cse.examination_place || '—' }}</td>
              <td>{{ cse.license_number || '—' }}</td>
              <td>
                <button @click="deleteCse(cse.id)" class="btn-del">Delete</button>
              </td>
            </tr>
            <tr v-if="!pds.civil_service_eligibilities?.length">
              <td colspan="6" class="no-records">No eligibility entries recorded.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Section V: Work Experience -->
      <div v-else-if="currentSection === 4" class="form-section">
        <div class="sub-header">
          <div>
            <h3>V. Work Experience (Item 28)</h3>
            <p class="section-sub">Teaching assignments, previous schools, and private practice</p>
          </div>
          <button @click="openModal('work')" class="btn-add">+ Add Work Experience</button>
        </div>

        <table class="sub-table">
          <thead>
            <tr>
              <th>Position Title</th>
              <th>Agency / School</th>
              <th>Inclusive Dates</th>
              <th>Salary / Grade</th>
              <th>Gov't?</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="we in pds.work_experiences" :key="we.id">
              <td><strong>{{ we.position_title }}</strong></td>
              <td>{{ we.department_agency_company }}</td>
              <td>{{ we.from_date }} to {{ we.to_present ? 'Present' : we.to_date }}</td>
              <td>{{ we.monthly_salary ? '₱' + we.monthly_salary : '—' }} ({{ we.salary_grade || '—' }})</td>
              <td>{{ we.is_government_service ? 'Yes' : 'No' }}</td>
              <td>
                <button @click="deleteWe(we.id)" class="btn-del">Delete</button>
              </td>
            </tr>
            <tr v-if="!pds.work_experiences?.length">
              <td colspan="6" class="no-records">No work experience entries recorded.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Section VI: Learning & Development -->
      <div v-else-if="currentSection === 5" class="form-section">
        <div class="sub-header">
          <div>
            <h3>VI. Learning & Development (Item 29)</h3>
            <p class="section-sub">Seminars, Teacher In-Service Trainings, and Certifications</p>
          </div>
          <button @click="openModal('ld')" class="btn-add">+ Add Training</button>
        </div>

        <table class="sub-table">
          <thead>
            <tr>
              <th>Training / Seminar Title</th>
              <th>Dates</th>
              <th>Hours</th>
              <th>Type</th>
              <th>Conducted / Sponsored By</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ld in pds.learning_developments" :key="ld.id">
              <td><strong>{{ ld.training_title }}</strong></td>
              <td>{{ ld.from_date }} to {{ ld.to_date }}</td>
              <td>{{ ld.number_of_hours }} hrs</td>
              <td>{{ ld.ld_type || '—' }}</td>
              <td>{{ ld.conducted_sponsored_by }}</td>
              <td>
                <button @click="deleteLd(ld.id)" class="btn-del">Delete</button>
              </td>
            </tr>
            <tr v-if="!pds.learning_developments?.length">
              <td colspan="6" class="no-records">No L&D trainings entered.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Section VII & VIII: Other Info & Declaration -->
      <div v-else-if="currentSection === 6" class="form-section">
        <h3>VIII. Other Information & Declaration</h3>
        <p class="section-sub">Government ID Verification & Affidavit</p>

        <form @submit.prevent="saveDeclaration">
          <h4 class="sub-heading">42. Government Issued Identification</h4>
          <div class="form-grid-3">
            <div class="field">
              <label>ID Type</label>
              <input v-model="formDecl.government_id_type" placeholder="e.g. PRC License, Passport, GSIS" />
            </div>
            <div class="field">
              <label>ID / License No.</label>
              <input v-model="formDecl.id_license_passport_no" />
            </div>
            <div class="field">
              <label>Date / Place of Issuance</label>
              <input v-model="formDecl.date_place_of_issuance" />
            </div>
          </div>

          <div class="declaration-box">
            <p>
              I declare under oath that I have personally accomplished this Personal Data Sheet which is a true,
              correct, and complete statement pursuant to the provisions of pertinent laws, rules, and regulations
              of the Republic of the Philippines.
            </p>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-save" :disabled="pdsStore.isSaving">
              Save Declaration
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Sub-modal for Education / Work / LD -->
    <div v-if="activeModal" class="modal-backdrop">
      <div class="modal-card glass-panel">
        <h3 v-if="activeModal === 'education'">Add Educational Background</h3>
        <h3 v-else-if="activeModal === 'eligibility'">Add Civil Service Eligibility</h3>
        <h3 v-else-if="activeModal === 'work'">Add Work Experience</h3>
        <h3 v-else-if="activeModal === 'ld'">Add L&D Intervention</h3>

        <!-- Education Form -->
        <form v-if="activeModal === 'education'" @submit.prevent="submitEdu">
          <div class="field">
            <label>Level</label>
            <select v-model="newEdu.level" required>
              <option value="Elementary">Elementary</option>
              <option value="Secondary">Secondary</option>
              <option value="Vocational/Trade Course">Vocational/Trade Course</option>
              <option value="College">College</option>
              <option value="Graduate Studies">Graduate Studies</option>
            </select>
          </div>
          <div class="field">
            <label>Name of School</label>
            <input v-model="newEdu.school_name" required />
          </div>
          <div class="field">
            <label>Degree / Course</label>
            <input v-model="newEdu.degree_course" />
          </div>
          <div class="form-grid-2">
            <div class="field">
              <label>From Year</label>
              <input v-model="newEdu.from_year" placeholder="yyyy" />
            </div>
            <div class="field">
              <label>To Year</label>
              <input v-model="newEdu.to_year" placeholder="yyyy" />
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" @click="activeModal = null" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-submit">Add Education</button>
          </div>
        </form>

        <!-- Eligibility Form -->
        <form v-else-if="activeModal === 'eligibility'" @submit.prevent="submitCse">
          <div class="field">
            <label>Eligibility Type</label>
            <input v-model="newCse.eligibility_type" placeholder="e.g. RA 1080 (Teacher Board Exam)" required />
          </div>
          <div class="form-grid-2">
            <div class="field">
              <label>Rating</label>
              <input v-model="newCse.rating" placeholder="e.g. 88.40" />
            </div>
            <div class="field">
              <label>Exam Date</label>
              <input v-model="newCse.examination_date" type="date" />
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" @click="activeModal = null" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-submit">Add Eligibility</button>
          </div>
        </form>

        <!-- Work Experience Form -->
        <form v-else-if="activeModal === 'work'" @submit.prevent="submitWork">
          <div class="field">
            <label>Position Title</label>
            <input v-model="newWork.position_title" required placeholder="e.g. Teacher I" />
          </div>
          <div class="field">
            <label>Department / School</label>
            <input v-model="newWork.department_agency_company" required />
          </div>
          <div class="form-grid-2">
            <div class="field">
              <label>From Date</label>
              <input v-model="newWork.from_date" type="date" />
            </div>
            <div class="field">
              <label>To Date</label>
              <input v-model="newWork.to_date" type="date" />
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" @click="activeModal = null" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-submit">Add Work Record</button>
          </div>
        </form>

        <!-- L&D Form -->
        <form v-else-if="activeModal === 'ld'" @submit.prevent="submitLd">
          <div class="field">
            <label>Training Title</label>
            <input v-model="newLd.training_title" required />
          </div>
          <div class="form-grid-2">
            <div class="field">
              <label>Number of Hours</label>
              <input v-model="newLd.number_of_hours" type="number" />
            </div>
            <div class="field">
              <label>Conducted By</label>
              <input v-model="newLd.conducted_sponsored_by" />
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" @click="activeModal = null" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-submit">Add Training</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, watch } from 'vue'
import { useRoute } from 'vue-router'
import { usePDSStore } from '@/stores/pds'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const pdsStore = usePDSStore()
const authStore = useAuthStore()

const loading = ref(true)
const pds = ref(null)
const currentSection = ref(0)
const activeModal = ref(null)

const sections = [
  { num: 'I', title: 'Personal Info' },
  { num: 'II', title: 'Family' },
  { num: 'III', title: 'Education' },
  { num: 'IV', title: 'Eligibility' },
  { num: 'V', title: 'Work Experience' },
  { num: 'VI', title: 'L&D / Training' },
  { num: 'VII', title: 'Declaration' },
]

const formPersonal = reactive({})
const formFamily = reactive({})
const formDecl = reactive({})

const newEdu = reactive({ level: 'College', school_name: '', degree_course: '', from_year: '', to_year: '' })
const newCse = reactive({ eligibility_type: '', rating: '', examination_date: '' })
const newWork = reactive({ position_title: '', department_agency_company: '', from_date: '', to_date: '' })
const newLd = reactive({ training_title: '', number_of_hours: 8, conducted_sponsored_by: '' })

const loadData = async () => {
  loading.value = true
  try {
    let teacherId = route.params.id
    let data = null
    if (teacherId) {
      data = await pdsStore.fetchPDSSummary(teacherId)
    } else {
      data = await pdsStore.fetchMyProfile()
    }
    if (data) {
      pds.value = data
      Object.assign(formPersonal, data.personal_info || {})
      Object.assign(formFamily, data.family_background || {})
      Object.assign(formDecl, data.pds_declaration || {})
    }
  } catch (err) {
    console.error('Failed to load profile data', err)
  } finally {
    loading.value = false
  }
}

const savePersonal = async () => {
  await pdsStore.savePersonalInfo(pds.value.id, formPersonal)
  alert('Personal Information updated successfully!')
}

const saveFamily = async () => {
  await pdsStore.saveFamilyBackground(pds.value.id, formFamily)
  alert('Family Background updated!')
}

const saveDeclaration = async () => {
  await pdsStore.saveDeclaration(pds.value.id, formDecl)
  alert('Declaration saved!')
}

const downloadPDF = () => {
  pdsStore.exportPDF(pds.value.id, pds.value.user?.full_name)
}

const openModal = (type) => {
  activeModal.value = type
}

const submitEdu = async () => {
  await pdsStore.addEducation(pds.value.id, newEdu)
  activeModal.value = null
}
const deleteEdu = async (id) => {
  if (confirm('Delete education record?')) await pdsStore.deleteEducation(pds.value.id, id)
}

const submitCse = async () => {
  await pdsStore.addEligibility(pds.value.id, newCse)
  activeModal.value = null
}
const deleteCse = async (id) => {
  if (confirm('Delete eligibility record?')) await pdsStore.deleteEligibility(pds.value.id, id)
}

const submitWork = async () => {
  await pdsStore.addWorkExperience(pds.value.id, newWork)
  activeModal.value = null
}
const deleteWe = async (id) => {
  if (confirm('Delete work experience?')) await pdsStore.deleteWorkExperience(pds.value.id, id)
}

const submitLd = async () => {
  await pdsStore.addLD(pds.value.id, newLd)
  activeModal.value = null
}
const deleteLd = async (id) => {
  if (confirm('Delete training record?')) await pdsStore.deleteLD(pds.value.id, id)
}

watch(() => route.params.id, () => {
  loadData()
})

onMounted(loadData)
</script>

<style scoped>
.pds-wizard-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.teacher-banner {
  padding: 1.5rem 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
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

.btn-export {
  background: var(--accent-gold);
  color: #0b1329;
  font-weight: 700;
  padding: 0.65rem 1.25rem;
  border-radius: var(--radius-sm);
}

.wizard-nav {
  display: flex;
  overflow-x: auto;
  padding: 0.5rem;
  gap: 0.5rem;
}

.nav-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1rem;
  background: transparent;
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  white-space: nowrap;
}

.tab-index {
  font-size: 0.75rem;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.08);
}

.nav-tab.active {
  background: var(--accent-gold);
  color: #0b1329;
  font-weight: 700;
}

.nav-tab.active .tab-index {
  background: #0b1329;
  color: var(--accent-gold);
}

.section-content {
  padding: 2rem;
}

.section-sub {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 1.5rem;
}

.sub-heading {
  font-size: 0.95rem;
  color: var(--accent-gold);
  margin: 1.75rem 0 1rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--border-color);
}

.form-grid-2 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-grid-3 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-grid-4 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.field label {
  display: block;
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-bottom: 0.35rem;
  font-weight: 500;
}

.form-actions {
  margin-top: 2rem;
  display: flex;
  justify-content: flex-end;
}

.btn-save {
  background: var(--accent-gold);
  color: #0b1329;
  font-weight: 700;
  padding: 0.75rem 2rem;
  border-radius: var(--radius-sm);
}

.sub-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.btn-add {
  background: var(--bg-surface-elevated);
  color: var(--accent-gold);
  border: 1px solid var(--accent-gold);
  padding: 0.45rem 1rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
}

.sub-table {
  width: 100%;
  border-collapse: collapse;
}

.sub-table th {
  text-align: left;
  font-size: 0.75rem;
  color: var(--text-muted);
  padding: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.sub-table td {
  padding: 0.85rem 0.75rem;
  font-size: 0.85rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.btn-del {
  background: rgba(244, 63, 94, 0.15);
  color: #fda4af;
  border: 1px solid rgba(244, 63, 94, 0.3);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.declaration-box {
  background: rgba(245, 158, 11, 0.08);
  border: 1px dashed var(--accent-gold);
  padding: 1.25rem;
  border-radius: var(--radius-md);
  margin: 1.5rem 0;
  font-size: 0.85rem;
  line-height: 1.6;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  width: 100%;
  max-width: 480px;
  padding: 2rem;
}

.modal-card h3 {
  margin-bottom: 1.5rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.btn-cancel {
  background: transparent;
  color: var(--text-secondary);
}

.btn-submit {
  background: var(--accent-gold);
  color: #0b1329;
  font-weight: 700;
  padding: 0.5rem 1.25rem;
  border-radius: var(--radius-sm);
}
</style>
