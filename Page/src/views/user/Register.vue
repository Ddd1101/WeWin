<template>
  <div class="main user-layout-register">
    <h3><span>{{ $t('user.register.register') }}</span></h3>
    <a-form ref="formRegister" :form="form" id="formRegister">
      <a-form-item>
        <a-input
          size="large"
          type="text"
          placeholder="请输入用户名"
          v-decorator="['username', {rules: [{ required: true, message: '请输入用户名' }], validateTrigger: ['change', 'blur']}]"
        ></a-input>
      </a-form-item>

      <a-form-item>
        <a-input-password
          size="large"
          placeholder="请输入密码"
          v-decorator="['password', {rules: [{ required: true, message: '请输入密码' }], validateTrigger: ['change', 'blur']}]"
        ></a-input-password>
      </a-form-item>

      <a-form-item>
        <a-input
          size="large"
          type="email"
          placeholder="请输入邮箱"
          v-decorator="['email', {rules: [{ type: 'email', message: '请输入有效的邮箱地址' }], validateTrigger: ['change', 'blur']}]"
        ></a-input>
      </a-form-item>

      <a-form-item>
        <a-input
          size="large"
          type="text"
          placeholder="请输入姓名"
          v-decorator="['first_name', {rules: [], validateTrigger: ['change', 'blur']}]"
        ></a-input>
      </a-form-item>

      <a-form-item>
        <a-select
          size="large"
          placeholder="请选择用户类型"
          v-decorator="['user_type', {rules: [{ required: true, message: '请选择用户类型' }], validateTrigger: ['change', 'blur']}]"
        >
          <a-select-option value="super_admin">网站超级管理员</a-select-option>
          <a-select-option value="site_admin">网站管理员</a-select-option>
          <a-select-option value="enterprise_admin">企业用户管理员</a-select-option>
          <a-select-option value="enterprise_user">企业用户普通账户</a-select-option>
          <a-select-option value="temporary">临时账户</a-select-option>
        </a-select>
      </a-form-item>

      <a-form-item>
        <a-button
          size="large"
          type="primary"
          htmlType="submit"
          class="register-button"
          :loading="registerBtn"
          @click.stop.prevent="handleSubmit"
          :disabled="registerBtn"
        >
          注册
        </a-button>
        <router-link class="login" :to="{ name: 'login' }">返回登录</router-link>
      </a-form-item>

    </a-form>
  </div>
</template>

<script>
import { register } from '@/api/accounts'
import { deviceMixin } from '@/store/device-mixin'

export default {
  name: 'Register',
  components: {
  },
  mixins: [deviceMixin],
  data () {
    return {
      form: this.$form.createForm(this),
      registerBtn: false
    }
  },
  methods: {
    handleSubmit () {
      const { form: { validateFields }, $router } = this
      validateFields({ force: true }, (err, values) => {
        if (!err) {
          this.registerBtn = true
          register(values).then(() => {
            this.$message.success('注册成功，请登录')
            $router.push({ name: 'login' })
            this.registerBtn = false
          }).catch(err => {
            this.$message.error('注册失败: ' + (err.response?.data?.error || err.message))
            this.registerBtn = false
          })
        }
      })
    }
  }
}
</script>

<style lang="less" scoped>
  .user-layout-register {
    & > h3 {
      font-size: 16px;
      margin-bottom: 20px;
    }
    .register-button {
      width: 50%;
    }
    .login {
      float: right;
      line-height: 40px;
    }
  }
</style>
