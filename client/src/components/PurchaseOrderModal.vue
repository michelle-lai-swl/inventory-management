<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && backlogItem" class="modal-overlay" @click="close">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">
              {{ mode === 'create' ? 'Create Purchase Order' : 'Purchase Order Details' }}
            </h3>
            <button class="close-button" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <!-- Item summary header -->
            <div class="item-header">
              <div class="item-icon">
                <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                  <rect x="8" y="8" width="32" height="32" rx="4" stroke="currentColor" stroke-width="2.5"/>
                  <path d="M16 24H32M24 16V32" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
                </svg>
              </div>
              <div class="item-title-section">
                <h4 class="item-name">{{ translateProductName(backlogItem.item_name) }}</h4>
                <div class="item-sku">SKU: {{ backlogItem.item_sku }}</div>
              </div>
              <span class="priority-badge" :class="backlogItem.priority">
                {{ backlogItem.priority }} Priority
              </span>
            </div>

            <!-- Shortage summary cards -->
            <div class="shortage-summary">
              <div class="summary-card danger">
                <div class="summary-label">Shortage</div>
                <div class="summary-value">{{ shortage }} units</div>
              </div>
              <div class="summary-card warning">
                <div class="summary-label">Days Delayed</div>
                <div class="summary-value">{{ backlogItem.days_delayed }} days</div>
              </div>
            </div>

            <!-- CREATE MODE: PO form -->
            <form v-if="mode === 'create'" class="po-form" @submit.prevent="submitPO">
              <div class="form-group">
                <label class="form-label" for="po-supplier">Supplier Name</label>
                <input
                  id="po-supplier"
                  v-model="form.supplier"
                  type="text"
                  class="form-input"
                  placeholder="Enter supplier name"
                  required
                />
              </div>

              <div class="form-group">
                <label class="form-label" for="po-quantity">Quantity to Order</label>
                <input
                  id="po-quantity"
                  v-model.number="form.quantity"
                  type="number"
                  class="form-input"
                  min="1"
                  required
                />
                <!-- Non-obvious: we pre-fill with the shortage so users start from the deficit -->
                <div class="form-hint">
                  Shortage: {{ shortage }} units (quantity_needed - quantity_available)
                </div>
              </div>

              <div class="form-group">
                <label class="form-label" for="po-delivery">Expected Delivery Date</label>
                <input
                  id="po-delivery"
                  v-model="form.expected_delivery"
                  type="date"
                  class="form-input"
                  :min="todayISO"
                  required
                />
              </div>

              <div v-if="formError" class="form-error">{{ formError }}</div>
            </form>

            <!-- VIEW MODE: read-only PO details or empty state -->
            <div v-else>
              <div v-if="backlogItem.purchase_order" class="po-details">
                <div class="info-grid">
                  <div class="info-item">
                    <div class="info-label">PO ID</div>
                    <div class="info-value po-id">{{ backlogItem.purchase_order.id }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">Supplier</div>
                    <div class="info-value">{{ backlogItem.purchase_order.supplier }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">Quantity Ordered</div>
                    <div class="info-value">{{ backlogItem.purchase_order.quantity }} units</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">Expected Delivery</div>
                    <div class="info-value">{{ formatDate(backlogItem.purchase_order.expected_delivery) }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">Created</div>
                    <div class="info-value">{{ formatDate(backlogItem.purchase_order.created_at) }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">Backlog Item ID</div>
                    <div class="info-value po-id">{{ backlogItem.purchase_order.backlog_item_id }}</div>
                  </div>
                </div>
              </div>

              <div v-else class="no-po">
                <div class="no-po-icon">
                  <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                    <rect x="6" y="6" width="28" height="28" rx="4" stroke="currentColor" stroke-width="2"/>
                    <path d="M14 20H26M20 14V26" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                </div>
                <p class="no-po-text">No PO on file</p>
                <p class="no-po-subtext">No purchase order has been raised for this backlog item.</p>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-secondary" @click="close">Close</button>
            <button
              v-if="mode === 'create'"
              type="submit"
              class="btn-primary"
              @click="submitPO"
            >
              Create Purchase Order
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from '../composables/useI18n'

const { translateProductName } = useI18n()

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  backlogItem: {
    type: Object,
    default: null
  },
  mode: {
    type: String,
    default: 'create'
    // 'create' | 'view'
  }
})

const emit = defineEmits(['close', 'po-created'])

// Shortage is the core quantity the PO should cover
const shortage = computed(() => {
  if (!props.backlogItem) return 0
  return props.backlogItem.quantity_needed - props.backlogItem.quantity_available
})

// Today in YYYY-MM-DD format for the date input min attribute
const todayISO = computed(() => new Date().toISOString().split('T')[0])

// Form state — reset whenever the modal opens with a new backlog item
const form = ref({
  supplier: '',
  quantity: 0,
  expected_delivery: ''
})

const formError = ref(null)

// Pre-fill the quantity with the shortage whenever the modal opens or the item changes
watch(
  () => [props.isOpen, props.backlogItem],
  ([open, item]) => {
    if (open && item) {
      form.value = {
        supplier: '',
        // Non-obvious: pre-fill with shortage so user sees the deficit amount up front
        quantity: item.quantity_needed - item.quantity_available,
        expected_delivery: ''
      }
      formError.value = null
    }
  },
  { immediate: true }
)

const close = () => {
  emit('close')
}

// Generate a simple UUID-like ID for the new PO
const generateId = () => {
  return 'PO-' + Date.now().toString(36).toUpperCase() + '-' + Math.random().toString(36).slice(2, 6).toUpperCase()
}

const submitPO = () => {
  formError.value = null

  if (!form.value.supplier.trim()) {
    formError.value = 'Supplier name is required.'
    return
  }
  if (!form.value.quantity || form.value.quantity < 1) {
    formError.value = 'Quantity must be at least 1.'
    return
  }
  if (!form.value.expected_delivery) {
    formError.value = 'Expected delivery date is required.'
    return
  }

  // Validate the delivery date is a real date
  const deliveryDate = new Date(form.value.expected_delivery)
  if (isNaN(deliveryDate.getTime())) {
    formError.value = 'Expected delivery date is invalid.'
    return
  }

  const poData = {
    id: generateId(),
    backlog_item_id: props.backlogItem.id,
    supplier: form.value.supplier.trim(),
    quantity: form.value.quantity,
    expected_delivery: form.value.expected_delivery,
    created_at: new Date().toISOString()
  }

  emit('po-created', poData)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  // Validate before formatting to avoid "Invalid Date" output
  if (isNaN(date.getTime())) return 'Invalid date'
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
  max-width: 700px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.close-button {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.close-button:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

.item-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 1.5rem;
}

.item-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.item-title-section {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.5rem 0;
}

.item-sku {
  font-size: 0.875rem;
  color: #64748b;
  font-family: 'Monaco', 'Courier New', monospace;
}

/* Priority badge colors match BacklogDetailModal */
.priority-badge {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  flex-shrink: 0;
}

.priority-badge.high {
  background: #fecaca;
  color: #991b1b;
}

.priority-badge.medium {
  background: #fed7aa;
  color: #92400e;
}

.priority-badge.low {
  background: #dbeafe;
  color: #1e40af;
}

.shortage-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.summary-card {
  padding: 1.25rem;
  border-radius: 10px;
  border: 2px solid;
}

.summary-card.danger {
  border-color: #fecaca;
  background: #fef2f2;
}

.summary-card.warning {
  border-color: #fed7aa;
  background: #fffbeb;
}

.summary-label {
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.summary-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: #0f172a;
}

.summary-card.danger .summary-value {
  color: #dc2626;
}

.summary-card.warning .summary-value {
  color: #f59e0b;
}

/* Form styles */
.po-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.form-input {
  padding: 0.625rem 0.875rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.938rem;
  color: #0f172a;
  background: white;
  font-family: inherit;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  outline: none;
}

.form-input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-hint {
  font-size: 0.813rem;
  color: #64748b;
}

.form-error {
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 0.875rem;
  font-weight: 500;
}

/* View mode: read-only PO details */
.po-details {
  padding-top: 0.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-label {
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.info-value {
  font-size: 0.938rem;
  color: #0f172a;
  font-weight: 500;
}

.info-value.po-id {
  font-family: 'Monaco', 'Courier New', monospace;
  color: #2563eb;
}

/* No PO empty state */
.no-po {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
  gap: 0.75rem;
}

.no-po-icon {
  color: #cbd5e1;
}

.no-po-text {
  font-size: 1.125rem;
  font-weight: 600;
  color: #334155;
  margin: 0;
}

.no-po-subtext {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
}

/* Footer */
.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-secondary {
  padding: 0.625rem 1.25rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.btn-secondary:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
}

.btn-primary {
  padding: 0.625rem 1.25rem;
  background: #2563eb;
  border: 1px solid #2563eb;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  color: white;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.btn-primary:hover {
  background: #1d4ed8;
  border-color: #1d4ed8;
}

/* Modal transition animations — same as BacklogDetailModal */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.2s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
}
</style>
