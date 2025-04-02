<template>
  <a-modal
    :visible="visible"
    :title="title"
    @cancel="handleCancel"
    :footer="null"
    width="800px"
  >
    <div class="terms-content">
      {{ content }}
    </div>
  </a-modal>
</template>

<script setup lang="ts">
defineProps<{
  visible: boolean
  title: string
  content: string
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
}>()

const handleCancel = () => {
  emit('update:visible', false)
}
</script>

<style scoped lang="scss">
.terms-content {
  max-height: 60vh;
  overflow-y: auto;
  white-space: pre-wrap;
  line-height: 1.6;
  padding: 16px;
}
</style> 