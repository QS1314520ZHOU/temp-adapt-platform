<template>
  <div class="field-picker-demo">
    <h2>字段映射配置工具</h2>
    <p class="desc">粘贴 JSON 数据，点击字段即可生成映射配置</p>

    <JsonFieldPicker @update:config="handleConfig" />

    <div v-if="generatedConfig" class="config-output">
      <h3>生成的配置</h3>
      <el-input type="textarea" :rows="10" :model-value="configJson" readonly />
      <el-button type="primary" @click="copyConfig" style="margin-top: 8px">复制配置</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import JsonFieldPicker from '@/components/JsonFieldPicker.vue'

const generatedConfig = ref<any>(null)

const configJson = computed(() => {
  return generatedConfig.value ? JSON.stringify(generatedConfig.value, null, 2) : ''
})

function handleConfig(config: any) {
  generatedConfig.value = config
}

function copyConfig() {
  navigator.clipboard.writeText(configJson.value)
  ElMessage.success('已复制到剪贴板')
}
</script>

<style scoped>
.field-picker-demo {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.desc {
  color: #909399;
  margin-bottom: 16px;
}

.config-output {
  margin-top: 24px;
}
</style>
