package com.wewin.app.ui.purchase

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.wewin.app.data.remote.RetrofitClient
import com.wewin.app.data.remote.dto.ErrorResponse
import com.wewin.app.data.remote.dto.MarkPartialRequest
import com.wewin.app.data.remote.dto.PurchaseListDto
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json
import java.io.IOException

data class PurchaseDetailUiState(
    val list: PurchaseListDto? = null,
    val isLoading: Boolean = false,
    val error: String? = null,
    val actionError: String? = null,
    val actionLoading: Boolean = false,
    val toast: String? = null
)

class PurchaseDetailViewModel(private val listId: Int) : ViewModel() {
    private val apiService = RetrofitClient.apiService

    private val _uiState = MutableStateFlow(PurchaseDetailUiState())
    val uiState: StateFlow<PurchaseDetailUiState> = _uiState.asStateFlow()

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        coerceInputValues = true
    }

    init {
        loadDetail()
    }

    fun loadDetail() {
        _uiState.update { it.copy(isLoading = true, error = null) }
        viewModelScope.launch {
            try {
                val response = apiService.getPurchaseListDetail(listId)
                if (response.isSuccessful) {
                    _uiState.update {
                        it.copy(list = response.body(), isLoading = false)
                    }
                } else {
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            error = parseError(response.code(), response.errorBody()?.string())
                        )
                    }
                }
            } catch (e: IOException) {
                _uiState.update {
                    it.copy(isLoading = false, error = "网络连接失败，请检查网络")
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(isLoading = false, error = "加载失败：${e.message ?: "未知错误"}")
                }
            }
        }
    }

    fun markPurchased(itemId: Int) {
        _uiState.update { it.copy(actionLoading = true, actionError = null) }
        viewModelScope.launch {
            try {
                val response = apiService.markItemPurchased(itemId)
                if (response.isSuccessful) {
                    _uiState.update { it.copy(actionLoading = false, toast = "已标记为已购买") }
                    loadDetail()
                } else {
                    _uiState.update {
                        it.copy(
                            actionLoading = false,
                            actionError = parseError(response.code(), response.errorBody()?.string())
                        )
                    }
                }
            } catch (e: IOException) {
                _uiState.update {
                    it.copy(actionLoading = false, actionError = "网络连接失败，请检查网络")
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(actionLoading = false, actionError = "操作失败：${e.message ?: "未知错误"}")
                }
            }
        }
    }

    fun markPartial(itemId: Int, purchasedQuantity: Double) {
        _uiState.update { it.copy(actionLoading = true, actionError = null) }
        viewModelScope.launch {
            try {
                val response = apiService.markItemPartial(
                    itemId,
                    MarkPartialRequest(purchasedQuantity)
                )
                if (response.isSuccessful) {
                    _uiState.update { it.copy(actionLoading = false, toast = "已标记为已购买部分") }
                    loadDetail()
                } else {
                    _uiState.update {
                        it.copy(
                            actionLoading = false,
                            actionError = parseError(response.code(), response.errorBody()?.string())
                        )
                    }
                }
            } catch (e: IOException) {
                _uiState.update {
                    it.copy(actionLoading = false, actionError = "网络连接失败，请检查网络")
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(actionLoading = false, actionError = "操作失败：${e.message ?: "未知错误"}")
                }
            }
        }
    }

    fun carryOverNextDay(itemId: Int) {
        _uiState.update { it.copy(actionLoading = true, actionError = null) }
        viewModelScope.launch {
            try {
                val response = apiService.carryOverNextDay(itemId)
                if (response.isSuccessful) {
                    _uiState.update {
                        it.copy(actionLoading = false, toast = "已添加到下一日采购清单")
                    }
                    loadDetail()
                } else {
                    _uiState.update {
                        it.copy(
                            actionLoading = false,
                            actionError = parseError(response.code(), response.errorBody()?.string())
                        )
                    }
                }
            } catch (e: IOException) {
                _uiState.update {
                    it.copy(actionLoading = false, actionError = "网络连接失败，请检查网络")
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(actionLoading = false, actionError = "操作失败：${e.message ?: "未知错误"}")
                }
            }
        }
    }

    fun clearToast() {
        _uiState.update { it.copy(toast = null) }
    }

    fun clearActionError() {
        _uiState.update { it.copy(actionError = null) }
    }

    private fun parseError(code: Int, errorBody: String?): String {
        if (errorBody.isNullOrEmpty()) {
            return httpErrorMessage(code)
        }
        return try {
            val errorResponse = json.decodeFromString(
                ErrorResponse.serializer(),
                errorBody
            )
            errorResponse.error ?: errorResponse.message ?: httpErrorMessage(code)
        } catch (e: Exception) {
            httpErrorMessage(code)
        }
    }

    private fun httpErrorMessage(code: Int): String = when (code) {
        401 -> "登录已过期，请重新登录"
        403 -> "没有权限执行此操作"
        404 -> "采购清单不存在"
        in 500..599 -> "服务器错误，请稍后重试"
        else -> "请求失败（$code）"
    }

    companion object {
        fun factory(listId: Int) = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                return PurchaseDetailViewModel(listId) as T
            }
        }
    }
}
