<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <!-- Success banner -->
      <div v-if="orderSuccess" class="success-banner">
        <span>{{ t('restocking.orderPlaced', { orderNumber: orderSuccess }) }}</span>
        <button class="banner-close" @click="orderSuccess = null">&times;</button>
      </div>

      <!-- Budget slider card -->
      <div class="card budget-card">
        <div class="budget-control">
          <div class="budget-value-row">
            <span class="budget-amount">{{ currencySymbol }}{{ budget.toLocaleString() }}</span>
            <span class="budget-label-text">{{ t('restocking.budgetLabel') }}</span>
          </div>
          <div class="budget-labels">
            <span>{{ t('restocking.budgetMin') }}</span>
            <span>{{ t('restocking.budgetMax') }}</span>
          </div>
          <!-- Debounce prevents excessive API calls while slider is being dragged -->
          <input
            type="range"
            min="1000"
            max="50000"
            step="500"
            v-model.number="budget"
            class="budget-slider"
          />
        </div>
      </div>

      <!-- Stats grid -->
      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.itemsToRestock') }}</div>
          <div class="stat-value">{{ recommendations.length }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t('restocking.totalCost') }}</div>
          <div class="stat-value">{{ currencySymbol }}{{ totalCost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">{{ t('restocking.budgetRemaining') }}</div>
          <div class="stat-value">{{ currencySymbol }}{{ budgetRemaining.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</div>
        </div>
        <div class="stat-card danger">
          <div class="stat-label">{{ t('restocking.highPriority') }}</div>
          <div class="stat-value">{{ increasingCount }}</div>
        </div>
      </div>

      <!-- Recommendations table card -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.itemsToRestock') }}</h3>
          <button
            class="place-order-btn"
            :disabled="ordering || recommendations.length === 0"
            @click="placeOrder"
          >
            {{ t('restocking.placeOrder') }}
          </button>
        </div>

        <div v-if="recommendations.length === 0" class="empty-state">
          <p>{{ t('restocking.noRecommendations') }}</p>
          <p class="empty-hint">{{ t('restocking.noRecommendationsHint') }}</p>
        </div>

        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.itemName') }}</th>
                <th>{{ t('restocking.table.currentDemand') }}</th>
                <th>{{ t('restocking.table.forecastedDemand') }}</th>
                <th>{{ t('restocking.table.demandGap') }}</th>
                <th>{{ t('restocking.table.trend') }}</th>
                <th>{{ t('restocking.table.qtyToOrder') }}</th>
                <th>{{ t('restocking.table.unitCost') }}</th>
                <th>{{ t('restocking.table.lineTotal') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in recommendations" :key="item.item_sku">
                <td><strong>{{ item.item_sku }}</strong></td>
                <td>{{ item.item_name }}</td>
                <td>{{ item.current_demand }}</td>
                <td><strong>{{ item.forecasted_demand }}</strong></td>
                <td>{{ item.demand_gap }}</td>
                <td>
                  <span :class="['badge', item.trend]">{{ item.trend }}</span>
                </td>
                <td>{{ item.recommended_quantity }}</td>
                <td>{{ currencySymbol }}{{ item.unit_cost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</td>
                <td><strong>{{ currencySymbol }}{{ item.line_total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency } = useI18n()

    const currencySymbol = computed(() => currentCurrency.value === 'JPY' ? '¥' : '$')

    const budget = ref(10000)
    const recommendationsData = ref([])
    const loading = ref(true)
    const error = ref(null)
    const ordering = ref(false)
    const orderSuccess = ref(null)

    const recommendations = computed(() => recommendationsData.value)

    const totalCost = computed(() =>
      recommendations.value.reduce((sum, r) => sum + r.line_total, 0)
    )

    const budgetRemaining = computed(() => budget.value - totalCost.value)

    const increasingCount = computed(() =>
      recommendations.value.filter(r => r.trend === 'increasing').length
    )

    const loadRecommendations = async () => {
      loading.value = true
      error.value = null
      try {
        const data = await api.getRestockingRecommendations(budget.value)
        recommendationsData.value = data
      } catch (err) {
        error.value = t('common.error')
        console.error(err)
      } finally {
        loading.value = false
      }
    }

    // Debounce prevents excessive API calls while slider is being dragged
    let debounceTimer = null
    watch(budget, () => {
      clearTimeout(debounceTimer)
      debounceTimer = setTimeout(() => loadRecommendations(), 300)
    })

    const placeOrder = async () => {
      const formattedTotal = currencySymbol.value + totalCost.value.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })

      const confirmed = window.confirm(
        t('restocking.confirmOrder', {
          count: recommendations.value.length,
          total: formattedTotal
        })
      )
      if (!confirmed) return

      ordering.value = true
      try {
        const orderData = {
          items: recommendations.value.map(r => ({
            item_sku: r.item_sku,
            item_name: r.item_name,
            quantity: r.recommended_quantity,
            unit_cost: r.unit_cost
          }))
        }
        const result = await api.createRestockingOrder(orderData)
        orderSuccess.value = result.order_number
        await loadRecommendations()
      } catch (err) {
        error.value = t('restocking.orderError')
        console.error(err)
      } finally {
        ordering.value = false
      }
    }

    onMounted(() => loadRecommendations())

    return {
      t,
      currencySymbol,
      budget,
      loading,
      error,
      ordering,
      orderSuccess,
      recommendations,
      totalCost,
      budgetRemaining,
      increasingCount,
      placeOrder
    }
  }
}
</script>

<style scoped>
/* Budget slider */
.budget-card { margin-bottom: 1rem; }
.budget-control { padding: 0.5rem 0; }
.budget-labels { display: flex; justify-content: space-between; font-size: 0.8rem; color: #64748b; margin-bottom: 0.5rem; }
.budget-value-row { display: flex; justify-content: center; align-items: baseline; gap: 0.5rem; margin-bottom: 0.75rem; }
.budget-amount { font-size: 1.75rem; font-weight: 700; color: #0f172a; }
.budget-label-text { font-size: 0.85rem; color: #64748b; }
.budget-slider { width: 100%; height: 6px; accent-color: #3b82f6; cursor: pointer; }

/* Place Order button */
.place-order-btn {
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.place-order-btn:hover:not(:disabled) { background: #2563eb; }
.place-order-btn:disabled { background: #94a3b8; cursor: not-allowed; }

/* Success / error banners */
.success-banner {
  background: #f0fdf4;
  border: 1px solid #86efac;
  border-radius: 8px;
  padding: 0.875rem 1.25rem;
  color: #166534;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.banner-close { background: none; border: none; font-size: 1.2rem; cursor: pointer; color: #166534; line-height: 1; }

/* Empty state */
.empty-state { text-align: center; padding: 2.5rem 1rem; color: #64748b; }
.empty-state p { margin-bottom: 0.5rem; }
.empty-hint { font-size: 0.85rem; color: #94a3b8; }

/* Card header flex for title + button */
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
