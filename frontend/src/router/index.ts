import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
  },
  {
    path: '/vendor',
    name: 'VendorList',
    component: () => import('@/views/VendorList.vue'),
  },
  {
    path: '/access-config',
    name: 'AccessConfig',
    component: () => import('@/views/AccessConfig.vue'),
  },
  {
    path: '/parser',
    name: 'MessageParser',
    component: () => import('@/views/MessageParser.vue'),
  },
  {
    path: '/record-locator',
    name: 'RecordLocator',
    component: () => import('@/views/RecordLocator.vue'),
  },
  {
    path: '/field-mapping',
    name: 'FieldMapping',
    component: () => import('@/views/FieldMapping.vue'),
  },
  {
    path: '/item-rule',
    name: 'ItemRuleConfig',
    component: () => import('@/views/ItemRuleConfig.vue'),
  },
  {
    path: '/preview',
    name: 'TransformPreview',
    component: () => import('@/views/TransformPreview.vue'),
  },
  {
    path: '/logs',
    name: 'RuntimeLog',
    component: () => import('@/views/RuntimeLog.vue'),
  },
  {
    path: '/unmatched',
    name: 'UnmatchedItem',
    component: () => import('@/views/UnmatchedItem.vue'),
  },
  {
    path: '/smartcare',
    name: 'SmartCareDatasource',
    component: () => import('@/views/SmartCareDatasource.vue'),
  },
  {
    path: '/smartcare-mapping',
    name: 'SmartCareFieldMapping',
    component: () => import('@/views/SmartCareFieldMapping.vue'),
  },
  {
    path: '/intake-output',
    name: 'IntakeOutputConfig',
    component: () => import('@/views/IntakeOutputConfig.vue'),
  },
  {
    path: '/intake-output-preview',
    name: 'IntakeOutputPreview',
    component: () => import('@/views/IntakeOutputPreview.vue'),
  },
  {
    path: '/callback',
    name: 'CallbackConfig',
    component: () => import('@/views/CallbackConfig.vue'),
  },
  {
    path: '/sync',
    name: 'SyncConfig',
    component: () => import('@/views/SyncConfig.vue'),
  },
  {
    path: '/department',
    name: 'DepartmentConfig',
    component: () => import('@/views/DepartmentConfig.vue'),
  },
  {
    path: '/field-picker',
    name: 'FieldPicker',
    component: () => import('@/views/FieldPickerDemo.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
