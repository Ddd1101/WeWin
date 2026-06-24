package com.wewin.app.data.local

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.wewin.app.data.remote.dto.UserInfo
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlinx.serialization.json.Json

private val Context.authDataStore: DataStore<Preferences> by preferencesDataStore(name = "auth_store")

class TokenStore(private val context: Context) {

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        coerceInputValues = true
    }

    val tokenFlow: Flow<String?> = context.authDataStore.data.map { prefs ->
        prefs[TOKEN_KEY]
    }

    val userFlow: Flow<UserInfo?> = context.authDataStore.data.map { prefs ->
        prefs[USER_KEY]?.let { json.decodeFromString(UserInfo.serializer(), it) }
    }

    suspend fun saveAuth(token: String, user: UserInfo) {
        context.authDataStore.edit { prefs ->
            prefs[TOKEN_KEY] = token
            prefs[USER_KEY] = json.encodeToString(UserInfo.serializer(), user)
        }
    }

    suspend fun clear() {
        context.authDataStore.edit { prefs ->
            prefs.remove(TOKEN_KEY)
            prefs.remove(USER_KEY)
        }
    }

    companion object {
        private val TOKEN_KEY = stringPreferencesKey("token")
        private val USER_KEY = stringPreferencesKey("user")
    }
}
