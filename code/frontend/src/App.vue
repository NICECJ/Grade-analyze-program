<template>
  <div id="app">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>成绩分析系统 (GradeInsights)</h1>
          <el-menu
            :default-active="$route.path"
            mode="horizontal"
            router
            class="nav-menu"
          >
            <el-sub-menu index="student">
              <template #title>
                <el-icon><UserFilled /></el-icon>
                学生管理
              </template>
              <el-menu-item index="/student-import">学生导入</el-menu-item>
              <el-menu-item index="/student-management">学生管理</el-menu-item>
            </el-sub-menu>
            <el-sub-menu index="import">
              <template #title>
                <el-icon><Upload /></el-icon>
                成绩导入
              </template>
              <el-menu-item index="/grade-import">自定义导入</el-menu-item>
              <el-menu-item index="/standard-template-import">标准模板导入</el-menu-item>
              <el-menu-item index="/manual-grade-import">手工录入</el-menu-item>
            </el-sub-menu>
            <el-menu-item index="/student-analysis">
              <el-icon><User /></el-icon>
              学生分析
            </el-menu-item>
            <el-menu-item index="/exam-list">
              <el-icon><List /></el-icon>
              考试管理
            </el-menu-item>
            <el-sub-menu index="ranking">
              <template #title>
                <el-icon><TrendCharts /></el-icon>
                排名分析
              </template>
              <el-menu-item index="/ranking">基础排名</el-menu-item>
              <el-menu-item index="/advanced-ranking">高级排名</el-menu-item>
            </el-sub-menu>
          </el-menu>
        </div>
      </el-header>
      
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

.el-header {
  background-color: #409EFF;
  color: white;
  padding: 0;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
}

.header-content h1 {
  margin: 0;
  font-size: 24px;
}

.nav-menu {
  background-color: transparent;
  border-bottom: none;
}

.nav-menu .el-menu-item {
  color: white;
  border-bottom: 2px solid transparent;
}

.nav-menu .el-menu-item:hover,
.nav-menu .el-menu-item.is-active {
  background-color: rgba(255, 255, 255, 0.1);
  border-bottom-color: white;
}

.el-main {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: calc(100vh - 60px);
}
</style>