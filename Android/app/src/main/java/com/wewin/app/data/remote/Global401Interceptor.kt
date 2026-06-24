package com.wewin.app.data.remote

import com.wewin.app.data.local.AuthEventBus
import com.wewin.app.data.local.TokenStore
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.Response

class Global401Interceptor(private val tokenStore: TokenStore) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val response = chain.proceed(chain.request())
        if (response.code == 401) {
            runBlocking { tokenStore.clear() }
            AuthEventBus.emitLogout()
        }
        return response
    }
}
