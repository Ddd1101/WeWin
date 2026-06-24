package com.wewin.app

import android.app.Application
import com.wewin.app.data.remote.RetrofitClient

class WeWinApp : Application() {
    override fun onCreate() {
        super.onCreate()
        RetrofitClient.init(this)
    }
}
