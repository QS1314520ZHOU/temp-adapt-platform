<template>
  <el-container class="app-container">
    <el-aside width="220px" class="app-aside">
      <div class="logo">
        <h2>体温单回传适配平台</h2>
      </div>
      <el-menu
        :default-active="route.path"
        router
        class="app-menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/">
          <el-icon><Monitor /></el-icon>
          <span>首页看板</span>
        </el-menu-item>
        <el-menu-item index="/vendor">
          <el-icon><OfficeBuilding /></el-icon>
          <span>厂家管理</span>
        </el-menu-item>
        <el-menu-item index="/access-config">
          <el-icon><Connection /></el-icon>
          <span>接入配置</span>
        </el-menu-item>
        <el-menu-item index="/parser">
          <el-icon><Document /></el-icon>
          <span>报文解析</span>
        </el-menu-item>
        <el-menu-item index="/record-locator">
          <el-icon><Aim /></el-icon>
          <span>记录定位</span>
        </el-menu-item>
        <el-menu-item index="/field-mapping">
          <el-icon><SetUp /></el-icon>
          <span>字段映射</span>
        </el-menu-item>
        <el-menu-item index="/item-rule">
          <el-icon><Setting /></el-icon>
          <span>指标规则</span>
        </el-menu-item>
        <el-menu-item index="/preview">
          <el-icon><View /></el-icon>
          <span>转换预览</span>
        </el-menu-item>
        <el-menu-item index="/logs">
          <el-icon><Notebook /></el-icon>
          <span>运行日志</span>
        </el-menu-item>
        <el-menu-item index="/unmatched">
          <el-icon><Warning /></el-icon>
          <span>未识别指标</span>
        </el-menu-item>
        <el-menu-item index="/smartcare">
          <el-icon><DataLine /></el-icon>
          <span>SmartCare数据源</span>
        </el-menu-item>
        <el-menu-item index="/smartcare-mapping">
          <el-icon><Share /></el-icon>
          <span>SmartCare字段映射</span>
        </el-menu-item>
        <el-menu-item index="/intake-output">
          <el-icon><Goods /></el-icon>
          <span>出入量配置</span>
        </el-menu-item>
        <el-menu-item index="/intake-output-preview">
          <el-icon><Histogram /></el-icon>
          <span>出入量预览</span>
        </el-menu-item>
        <el-menu-item index="/callback">
          <el-icon><Promotion /></el-icon>
          <span>回传配置</span>
        </el-menu-item>
        <el-menu-item index="/sync">
          <el-icon><Timer /></el-icon>
          <span>同步任务</span>
        </el-menu-item>
        <el-menu-item index="/department">
          <el-icon><OfficeBuilding /></el-icon>
          <span>科室配置</span>
        </el-menu-item>
        <el-menu-item index="/field-picker">
          <el-icon><Pointer /></el-icon>
          <span>字段提取工具</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="app-header">
        <h1>体温单回传适配平台</h1>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import {
  Monitor,
  OfficeBuilding,
  Connection,
  Document,
  Aim,
  SetUp,
  Setting,
  View,
  Notebook,
  Warning,
  DataLine,
  Share,
  Goods,
  Histogram,
  Promotion,
  Timer,
  Pointer,
} from '@element-plus/icons-vue'

const route = useRoute()
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', Arial, sans-serif;
}

.app-container {
  height: 100%;
}

.app-aside {
  background-color: #304156;
  overflow-y: auto;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background-color: #263445;
}

.logo h2 {
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.app-menu {
  border-right: none;
}

.app-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  padding: 0 20px;
  height: 60px;
}

.app-header h1 {
  font-size: 18px;
  color: #333;
  font-weight: 600;
}

.app-main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>
