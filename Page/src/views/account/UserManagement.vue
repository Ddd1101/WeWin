<template>
  <a-card :bordered="false">
    <div class="table-page-search-wrapper">
      <a-form layout="inline">
        <a-row :gutter="48">
          <a-col :md="6" :sm="24">
            <a-form-item label="用户名">
              <a-input v-model="queryParam.username" placeholder="请输入用户名" />
            </a-form-item>
          </a-col>
          <a-col :md="6" :sm="24">
            <a-form-item label="用户类型">
              <a-select v-model="queryParam.user_type" placeholder="请选择" allow-clear>
                <a-select-option value="super_admin">网站超级管理员</a-select-option>
                <a-select-option value="site_admin">网站管理员</a-select-option>
                <a-select-option value="enterprise_admin">企业用户管理员</a-select-option>
                <a-select-option value="enterprise_user">企业用户普通账户</a-select-option>
                <a-select-option value="temporary">临时账户</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :md="12" :sm="24">
            <span class="table-page-search-submitButtons">
              <a-button type="primary" @click="loadData">查询</a-button>
              <a-button style="margin-left: 8px" @click="resetQuery">重置</a-button>
              <a-button type="primary" style="margin-left: 8px" @click="handleAdd">新增用户</a-button>
            </span>
          </a-col>
        </a-row>
      </a-form>
    </div>

    <s-table
      ref="table"
      row-key="id"
      size="default"
      :columns="columns"
      :data="loadData"
    >
      <a-tag color="blue" slot="user_type" slot-scope="text">{{ getUserTypeText(text) }}</a-tag>
      <span slot="action" slot-scope="text, record">
        <a @click="handleEdit(record)">编辑</a>
        <a-divider type="vertical" />
        <a-popconfirm
          title="确定要删除这个用户吗？"
          @confirm="handleDelete(record)"
        >
          <a style="color: red">删除</a>
        </a-popconfirm>
      </span>
    </s-table>
  </a-card>
</template>

<script>
import { STable } from '@/components'
import { getUserList } from '@/api/accounts'
import { message } from 'ant-design-vue'

const columns = [
  {
    title: 'ID',
    dataIndex: 'id',
    width: 80
  },
  {
    title: '用户名',
    dataIndex: 'username'
  },
  {
    title: '姓名',
    dataIndex: 'first_name'
  },
  {
    title: '邮箱',
    dataIndex: 'email'
  },
  {
    title: '用户类型',
    dataIndex: 'user_type',
    scopedSlots: { customRender: 'user_type' }
  },
  {
    title: '操作',
    width: '150px',
    dataIndex: 'action',
    scopedSlots: { customRender: 'action' }
  }
]

const userTypeMap = {
  'super_admin': '网站超级管理员',
  'site_admin': '网站管理员',
  'enterprise_admin': '企业用户管理员',
  'enterprise_user': '企业用户普通账户',
  'temporary': '临时账户'
}

export default {
  name: 'UserManagement',
  components: {
    STable
  },
  data () {
    return {
      queryParam: {
        username: '',
        user_type: ''
      },
      columns,
      loadData: parameter => {
        return getUserList(parameter).then(res => {
          return {
            data: res.results || res,
            pageSize: parameter.pageSize,
            pageNo: parameter.pageNo,
            total: res.count || (res.results ? res.count : res.length)
          }
        })
      }
    }
  },
  methods: {
    getUserTypeText (type) {
      return userTypeMap[type] || type
    },
    resetQuery () {
      this.queryParam = {
        username: '',
        user_type: ''
      }
      if (this.$refs.table) {
        this.$refs.table.refresh(true)
      }
    },
    handleAdd () {
      message.info('新增用户功能待实现')
    },
    handleEdit (record) {
      message.info('编辑用户功能待实现')
    },
    handleDelete (record) {
      message.info('删除用户功能待实现')
    }
  }
}
</script>

<style lang="less" scoped>
</style>
