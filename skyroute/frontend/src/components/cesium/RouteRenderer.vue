<script setup lang="ts">
// Route rendering is handled by CesiumViewer.vue directly
// This component can be used for additional route visualization
defineProps<{ taskId?: string }>()
</script>
<template><slot /></template>
