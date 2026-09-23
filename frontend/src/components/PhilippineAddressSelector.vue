<template>
  <div class="ph-address-selector">
    <div class="selector-mode-bar">
      <span class="mode-label">
        <span class="icon">📍</span> Philippine Administrative Address (Cascading PSGC)
      </span>
      <button
        type="button"
        @click="toggleMode"
        class="btn-mode-toggle"
        :title="manualMode ? 'Switch to Cascading Dropdowns' : 'Switch to Manual Free Text'"
      >
        {{ manualMode ? '🔄 Use Cascading Selectors' : '✏️ Edit as Plain Text' }}
      </button>
    </div>

    <!-- CASCADING SELECTORS MODE -->
    <div v-if="!manualMode" class="cascading-grid">
      <!-- 1. Region -->
      <div class="field">
        <label>Region</label>
        <select
          v-model="selectedRegion"
          @change="onRegionChange"
          :disabled="disabled || loadingRegions"
          class="form-select"
        >
          <option value="">{{ loadingRegions ? 'Loading regions...' : 'Select Region' }}</option>
          <option v-for="r in regions" :key="r.name" :value="r.name">
            {{ r.designation }} — {{ r.name }}
          </option>
        </select>
      </div>

      <!-- 2. Province -->
      <div class="field">
        <label>Province *</label>
        <select
          v-model="selectedProvince"
          @change="onProvinceChange"
          :disabled="disabled || loadingProvinces || !provinces.length"
          class="form-select"
        >
          <option value="">{{ loadingProvinces ? 'Loading provinces...' : (selectedRegion ? 'Select Province' : 'Select Region first') }}</option>
          <option v-for="p in provinces" :key="p.name" :value="p.name">
            {{ p.name }}
          </option>
        </select>
      </div>

      <!-- 3. City / Municipality -->
      <div class="field">
        <label>City / Municipality *</label>
        <select
          v-model="selectedCity"
          @change="onCityChange"
          :disabled="disabled || loadingCities || !cities.length"
          class="form-select"
        >
          <option value="">{{ loadingCities ? 'Loading cities...' : (selectedProvince ? 'Select City/Municipality' : 'Select Province first') }}</option>
          <option v-for="c in cities" :key="c.name" :value="c.name">
            {{ c.name }} {{ c.city ? '(City)' : '' }}
          </option>
        </select>
      </div>

      <!-- 4. Barangay -->
      <div class="field">
        <label>Barangay *</label>
        <select
          v-model="selectedBarangay"
          @change="onBarangayChange"
          :disabled="disabled || loadingBarangays || !barangays.length"
          class="form-select"
        >
          <option value="">{{ loadingBarangays ? 'Loading barangays...' : (selectedCity ? 'Select Barangay' : 'Select City first') }}</option>
          <option v-for="b in barangays" :key="b.code || b.name" :value="b.name">
            {{ b.name }}
          </option>
        </select>
      </div>

      <!-- 5. ZIP Code -->
      <div class="field zip-field">
        <label>ZIP CODE</label>
        <input
          type="text"
          :value="zipCode"
          @input="$emit('update:zipCode', $event.target.value)"
          placeholder="e.g. 3500"
          :disabled="disabled"
          class="form-input"
        />
      </div>
    </div>

    <!-- MANUAL TEXT INPUT MODE -->
    <div v-else class="manual-grid">
      <div class="field">
        <label>Province</label>
        <input
          type="text"
          :value="province"
          @input="$emit('update:province', $event.target.value)"
          placeholder="Province"
          :disabled="disabled"
          class="form-input"
        />
      </div>
      <div class="field">
        <label>City / Municipality</label>
        <input
          type="text"
          :value="cityMunicipality"
          @input="$emit('update:cityMunicipality', $event.target.value)"
          placeholder="City / Municipality"
          :disabled="disabled"
          class="form-input"
        />
      </div>
      <div class="field">
        <label>Barangay</label>
        <input
          type="text"
          :value="barangay"
          @input="$emit('update:barangay', $event.target.value)"
          placeholder="Barangay"
          :disabled="disabled"
          class="form-input"
        />
      </div>
      <div class="field zip-field">
        <label>ZIP CODE</label>
        <input
          type="text"
          :value="zipCode"
          @input="$emit('update:zipCode', $event.target.value)"
          placeholder="ZIP Code"
          :disabled="disabled"
          class="form-input"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '@/api'

const props = defineProps({
  province: { type: String, default: '' },
  cityMunicipality: { type: String, default: '' },
  barangay: { type: String, default: '' },
  zipCode: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits([
  'update:province',
  'update:cityMunicipality',
  'update:barangay',
  'update:zipCode',
  'change',
])

const manualMode = ref(false)

// Options lists
const regions = ref([])
const provinces = ref([])
const cities = ref([])
const barangays = ref([])

// Current selections in cascading mode
const selectedRegion = ref('')
const selectedProvince = ref('')
const selectedCity = ref('')
const selectedBarangay = ref('')

// Loading states
const loadingRegions = ref(false)
const loadingProvinces = ref(false)
const loadingCities = ref(false)
const loadingBarangays = ref(false)

const toggleMode = () => {
  manualMode.value = !manualMode.value
}

// Fetch all regions on mount
const loadRegions = async () => {
  loadingRegions.value = true
  try {
    const res = await api.get('/address/regions/')
    regions.value = res.data || []
  } catch (err) {
    console.error('Failed to load regions:', err)
  } finally {
    loadingRegions.value = false
  }
}

// When Region changes
const onRegionChange = async () => {
  selectedProvince.value = ''
  selectedCity.value = ''
  selectedBarangay.value = ''
  provinces.value = []
  cities.value = []
  barangays.value = []

  emit('update:province', '')
  emit('update:cityMunicipality', '')
  emit('update:barangay', '')

  if (!selectedRegion.value) return

  loadingProvinces.value = true
  try {
    const res = await api.get('/address/provinces/', { params: { region: selectedRegion.value } })
    provinces.value = res.data || []
  } catch (err) {
    console.error('Failed to load provinces:', err)
  } finally {
    loadingProvinces.value = false
  }
}

// When Province changes
const onProvinceChange = async () => {
  selectedCity.value = ''
  selectedBarangay.value = ''
  cities.value = []
  barangays.value = []

  emit('update:province', selectedProvince.value)
  emit('update:cityMunicipality', '')
  emit('update:barangay', '')
  emit('change')

  if (!selectedProvince.value) return

  loadingCities.value = true
  try {
    const res = await api.get('/address/cities/', { params: { province: selectedProvince.value } })
    cities.value = res.data || []
  } catch (err) {
    console.error('Failed to load cities:', err)
  } finally {
    loadingCities.value = false
  }
}

// When City changes
const onCityChange = async () => {
  selectedBarangay.value = ''
  barangays.value = []

  emit('update:cityMunicipality', selectedCity.value)
  emit('update:barangay', '')

  // Auto-suggest zip code if available in city data
  const matchedCity = cities.value.find(c => c.name.toLowerCase() === selectedCity.value.toLowerCase())
  if (matchedCity?.zip_code) {
    emit('update:zipCode', matchedCity.zip_code)
  }
  emit('change')

  if (!selectedCity.value) return

  loadingBarangays.value = true
  try {
    const res = await api.get('/address/barangays/', { params: { city: selectedCity.value } })
    barangays.value = res.data || []
  } catch (err) {
    console.error('Failed to load barangays:', err)
  } finally {
    loadingBarangays.value = false
  }
}

// When Barangay changes
const onBarangayChange = () => {
  emit('update:barangay', selectedBarangay.value)
  emit('change')
}

// Sync external props (e.g. loaded from API) with cascading selects
const syncFromProps = async () => {
  if (!props.province) {
    selectedProvince.value = ''
    selectedCity.value = ''
    selectedBarangay.value = ''
    return
  }

  // If regions not loaded yet, wait
  if (!regions.value.length) {
    await loadRegions()
  }

  // If province is provided, try to find which region it belongs to
  if (props.province && props.province !== selectedProvince.value) {
    try {
      // Fetch all provinces to find region
      const allProvRes = await api.get('/address/provinces/')
      const foundProv = (allProvRes.data || []).find(p => p.name.toLowerCase() === props.province.toLowerCase())
      if (foundProv) {
        // Find region designation or name
        const foundReg = regions.value.find(r => r.designation.toLowerCase() === foundProv.region.toLowerCase() || r.name.toLowerCase() === foundProv.region.toLowerCase())
        if (foundReg) {
          selectedRegion.value = foundReg.name
        }
        // Fetch provinces for this region
        const provRes = await api.get('/address/provinces/', { params: { region: selectedRegion.value } })
        provinces.value = provRes.data || []
        selectedProvince.value = foundProv.name

        // Fetch cities
        const citiesRes = await api.get('/address/cities/', { params: { province: foundProv.name } })
        cities.value = citiesRes.data || []

        if (props.cityMunicipality) {
          const foundCity = cities.value.find(c => c.name.toLowerCase() === props.cityMunicipality.toLowerCase() || props.cityMunicipality.toLowerCase().includes(c.name.toLowerCase()))
          if (foundCity) {
            selectedCity.value = foundCity.name
            // Fetch barangays
            const bgyRes = await api.get('/address/barangays/', { params: { city: foundCity.name } })
            barangays.value = bgyRes.data || []
            if (props.barangay) {
              const foundBgy = barangays.value.find(b => b.name.toLowerCase() === props.barangay.toLowerCase())
              if (foundBgy) {
                selectedBarangay.value = foundBgy.name
              } else {
                selectedBarangay.value = props.barangay
              }
            }
          } else {
            selectedCity.value = props.cityMunicipality
          }
        }
      } else {
        // Not found in PSGC list, user might have typed custom name
        selectedProvince.value = props.province
        selectedCity.value = props.cityMunicipality
        selectedBarangay.value = props.barangay
      }
    } catch (e) {
      console.error('Error syncing address from props:', e)
    }
  } else {
    selectedProvince.value = props.province
    selectedCity.value = props.cityMunicipality
    selectedBarangay.value = props.barangay
  }
}

watch(
  () => [props.province, props.cityMunicipality, props.barangay],
  () => {
    if (props.province !== selectedProvince.value || props.cityMunicipality !== selectedCity.value || props.barangay !== selectedBarangay.value) {
      syncFromProps()
    }
  },
  { deep: true }
)

onMounted(async () => {
  await loadRegions()
  await syncFromProps()
})
</script>

<style scoped>
.ph-address-selector {
  margin-top: 0.5rem;
  margin-bottom: 0.75rem;
}

.selector-mode-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.6rem;
  padding: 0.35rem 0.6rem;
  background: rgba(14, 165, 233, 0.08);
  border: 1px solid rgba(14, 165, 233, 0.2);
  border-radius: 6px;
}

.mode-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #38bdf8;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.btn-mode-toggle {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #e2e8f0;
  font-size: 0.72rem;
  font-weight: 500;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-mode-toggle:hover {
  background: rgba(14, 165, 233, 0.2);
  border-color: #38bdf8;
  color: #ffffff;
}

.cascading-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr 1.1fr 1.1fr 0.6fr;
  gap: 0.75rem;
}

.manual-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 0.6fr;
  gap: 0.75rem;
}

.field {
  display: flex;
  flex-direction: column;
}

.field label {
  font-size: 0.76rem;
  font-weight: 600;
  color: #94a3b8;
  margin-bottom: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.form-select,
.form-input {
  width: 100%;
  padding: 0.55rem 0.75rem;
  background: rgba(15, 23, 42, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 6px;
  color: #f1f5f9;
  font-size: 0.85rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-select:focus,
.form-input:focus {
  outline: none;
  border-color: #38bdf8;
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
}

.form-select:disabled,
.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: rgba(15, 23, 42, 0.4);
}

@media (max-width: 900px) {
  .cascading-grid {
    grid-template-columns: 1fr 1fr;
  }
  .manual-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 600px) {
  .cascading-grid,
  .manual-grid {
    grid-template-columns: 1fr;
  }
}
</style>
