package com.wewin.app.ui.purchase

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.wewin.app.data.remote.RetrofitClient
import com.wewin.app.data.remote.dto.CreatePurchaseItemRequest
import com.wewin.app.data.remote.dto.CreatePurchaseListRequest
import com.wewin.app.data.remote.dto.ErrorResponse
import com.wewin.app.data.remote.dto.PurchaseListSummaryDto
import com.wewin.app.data.remote.dto.UserBriefDto
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json
import java.io.IOException

/**
 * 调用方传入的预填数据：商品/SKU 信息 + 默认值
 */
data class PurchasePrefillData(
    val productId: Int? = null,
    val skuId: Int? = null,
    val productType: String,        // "bead" / "accessory"
    val productName: String,
    val skuCode: String = "",
    val defaultUnit: String,        // "克" / "件"
    val defaultUnitPrice: Double,   // 串珠用 purchase_cost(克价)，配件用 cost_price
    val supplier: String = "",
    val location: String = "",
    val qualityLevel: Int? = null,
    val material: String = "",
    val size: Int? = null,
    val color: String = ""
)

data class AddToPurchaseUiState(
    val isLoading: Boolean = false,
    val isSubmitting: Boolean = false,
    val error: String? = null,
    val users: List<UserBriefDto> = emptyList(),
    val uncompletedLists: List<PurchaseListSummaryDto> = emptyList(),
    val usersLoaded: Boolean = false,
    val listsLoaded: Boolean = false,
    val success: Boolean = false
)

class AddToPurchaseViewModel : ViewModel() {
    private val apiService = RetrofitClient.apiService

    private val _uiState = MutableStateFlow(AddToPurchaseUiState())
    val uiState: StateFlow<AddToPurchaseUiState> = _uiState.asStateFlow()

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        coerceInputValues = true
    }

    fun loadOptions() {
        loadUsers()
        loadUncompletedLists()
    }

    private fun loadUsers() {
        viewModelScope.launch {
            try {
                val response = apiService.getUsers()
                if (response.isSuccessful) {
                    _uiState.update {
                        it.copy(
                            users = response.body()?.users ?: emptyList(),
                            usersLoaded = true
                        )
                    }
                } else {
                    _uiState.update {
                        it.copy(
                            usersLoaded = true,
                            error = parseError(response.code(), response.errorBody()?.string())
                        )
                    }
                }
            } catch (e: IOException) {
                _uiState.update {
                    it.copy(
                        usersLoaded = true,
                        error = "网络连接失败，请检查网络"
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        usersLoaded = true,
                        error = "加载员工列表失败：${e.message ?: "未知错误"}"
                    )
                }
            }
        }
    }

    private fun loadUncompletedLists() {
        viewModelScope.launch {
            try {
                val response = apiService.getUncompletedLists()
                if (response.isSuccessful) {
                    _uiState.update {
                        it.copy(
                            uncompletedLists = response.body()?.lists ?: emptyList(),
                            listsLoaded = true
                        )
                    }
                } else {
                    _uiState.update {
                        it.copy(
                            listsLoaded = true,
                            error = parseError(response.code(), response.errorBody()?.string())
                        )
                    }
                }
            } catch (e: IOException) {
                _uiState.update {
                    it.copy(
                        listsLoaded = true,
                        error = "网络连接失败，请检查网络"
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        listsLoaded = true,
                        error = "加载未完成清单失败：${e.message ?: "未知错误"}"
                    )
                }
            }
        }
    }

    fun createNewListAndAddItem(
        title: String,
        assigneeId: Int,
        plannedDate: String,
        notes: String,
        item: CreatePurchaseItemRequest
    ) {
        if (_uiState.value.isSubmitting) return
        _uiState.update { it.copy(isSubmitting = true, error = null) }
        viewModelScope.launch {
            try {
                val request = CreatePurchaseListRequest(
                    title = title,
                    assigneeId = assigneeId,
                    plannedDate = plannedDate,
                    notes = notes,
                    items = listOf(item)
                )
                val response = apiService.createPurchaseList(request)
                if (response.isSuccessful) {
                    _uiState.update {
                        it.copy(isSubmitting = false, success = true)
                    }
                } else {
                    _uiState.update {
                        it.copy(
                            isSubmitting = false,
                            error = parseError(response.code(), response.errorBody()?.string())
                        )
                    }
                }
            } catch (e: IOException) {
                _uiState.update {
                    it.copy(isSubmitting = false, error = "网络连接失败，请检查网络")
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isSubmitting = false,
                        error = "创建清单失败：${e.message ?: "未知错误"}"
                    )
                }
            }
        }
    }

    fun addItemToExistingList(listId: Int, item: CreatePurchaseItemRequest) {
        if (_uiState.value.isSubmitting) return
        _uiState.update { it.copy(isSubmitting = true, error = null) }
        viewModelScope.launch {
            try {
                val response = apiService.addPurchaseItem(listId, item)
                if (response.isSuccessful) {
                    _uiState.update {
                        it.copy(isSubmitting = false, success = true)
                    }
                } else {
                    _uiState.update {
                        it.copy(
                            isSubmitting = false,
                            error = parseError(response.code(), response.errorBody()?.string())
                        )
                    }
                }
            } catch (e: IOException) {
                _uiState.update {
                    it.copy(isSubmitting = false, error = "网络连接失败，请检查网络")
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isSubmitting = false,
                        error = "加入清单失败：${e.message ?: "未知错误"}"
                    )
                }
            }
        }
    }

    fun reset() {
        _uiState.update {
            it.copy(success = false, error = null, isSubmitting = false)
        }
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
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
        404 -> "资源不存在"
        in 500..599 -> "服务器错误，请稍后重试"
        else -> "请求失败（$code）"
    }
}
