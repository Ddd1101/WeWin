package com.wewin.app.data.remote

import android.content.Context
import com.jakewharton.retrofit2.converter.kotlinx.serialization.asConverterFactory
import com.wewin.app.BuildConfig
import com.wewin.app.data.local.TokenStore
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import java.util.concurrent.TimeUnit

object RetrofitClient {

    @Volatile
    private var _apiService: ApiService? = null

    fun init(context: Context) {
        if (_apiService != null) return

        synchronized(this) {
            if (_apiService != null) return

            val tokenStore = TokenStore(context.applicationContext)

            val loggingInterceptor = HttpLoggingInterceptor().apply {
                level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BASIC else HttpLoggingInterceptor.Level.NONE
                redactHeader("Authorization")
            }

            val okHttpClient = OkHttpClient.Builder()
                .addInterceptor { chain ->
                    if (chain.request().body is okhttp3.MultipartBody) {
                        chain.withReadTimeout(180, TimeUnit.SECONDS)
                            .withWriteTimeout(180, TimeUnit.SECONDS)
                            .proceed(chain.request())
                    } else chain.proceed(chain.request())
                }
                .addInterceptor(AuthInterceptor(tokenStore))
                .addInterceptor(Global401Interceptor(tokenStore))
                .addInterceptor(loggingInterceptor)
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .build()

            val json = Json {
                ignoreUnknownKeys = true
                isLenient = true
                coerceInputValues = true
            }

            val baseUrl = ensureTrailingSlash(BuildConfig.API_BASE_URL)

            val retrofit = Retrofit.Builder()
                .baseUrl(baseUrl)
                .client(okHttpClient)
                .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
                .build()

            _apiService = retrofit.create(ApiService::class.java)
        }
    }

    val apiService: ApiService
        get() = _apiService ?: error("RetrofitClient 未初始化，请先在 Application.onCreate 中调用 RetrofitClient.init(context)")

    private fun ensureTrailingSlash(url: String): String {
        return if (url.endsWith("/")) url else "$url/"
    }
}
