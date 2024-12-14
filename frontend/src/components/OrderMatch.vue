<template>
  <tr>
    <td>{{ competition.sport }}</td>
    <td>{{ competition.name }}</td>
    <td style="margin-bottom: 5px">
      <strong>{{ local.name }}</strong> ({{ local.country }}) vs
      <strong>{{ visitor.name }}</strong> ({{ visitor.country }})
    </td>
    <td>
      <span class="quantity-controls">
        <button
          type="button"
          class="btn btn-sm btn-danger"
          @click="decrementQuantity"
          :disabled="quantity === 1">
          -
        </button>
        <span class="quantity">{{ quantity }}</span>
        <button
          type="button"
          class="btn btn-sm btn-success"
          @click="incrementQuantity"
          :disabled="quantity === tickets">
          +
        </button>
      </span>
    </td>
    <td>{{ price }}</td>
    <td>{{ price * quantity }}</td>
    <td>
      <button type="button" class="btn btn-sm btn-danger" @click="removeFromCart">Eliminar Entrada</button>
    </td>
  </tr>
</template>

<script>
export default {
  name: 'OrderMatch',
  props: ['id', 'competition', 'local', 'visitor', 'price', 'tickets', 'quantity'],
  methods: {
    incrementQuantity () {
      if (this.quantity < this.tickets) {
        this.quantity++
        this.$emit('update-quantity', { id: this.id, quantity: this.quantity })
      }
    },
    decrementQuantity () {
      if (this.quantity > 1) {
        this.quantity--
        this.$emit('update-quantity', { id: this.id, quantity: this.quantity })
      }
    },
    removeFromCart () {
      this.$emit('remove-from-cart', { id: this.id })
    }
  }
}
</script>

<style scoped>
.quantity-controls {
  display: flex;
  align-items: center;
}

.quantity {
  margin: 0 10px;
  display: inline-block;
  min-width: 20px;
  text-align: center;
}
</style>
