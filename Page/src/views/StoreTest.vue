<template>
  <div class="store-test">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>店铺测试页面</span>
        </div>
      </template>
      <div class="content">
        <el-empty description="这是店铺管理下的测试页面" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content {
  padding: 40px;
}
</style>
