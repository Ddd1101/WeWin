package com.wewin.app.ui.purchase

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.wewin.app.data.remote.RetrofitClient
import com.wewin.app.data.remote.dto.ErrorResponse
import com.wewin.app.data.remote.dto.PurchaseListDto
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json
import java.io.IOException

enum class PurchaseStatusFilter(val value: String?, val label: String) {
    ALL(null, "全部"),
    PENDING("pending", "待采购"),
    IN_PROGRESS("in_progress", "进行中"),
    COMPLETED("completed", "已完成")
}

enum class PurchaseAssigneeScope(val value: String, val label: String) {
    MY_ASSIGNED("my_assigned", "指派给我"),
    MINE("mine", "我指派的"),
    ALL("all", "全部")
}

data class PurchaseListUiState(
    val lists: List<PurchaseListDto> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val statusFilter: PurchaseStatusFilter = PurchaseStatusFilter.ALL,
    val assigneeScope: PurchaseAssigneeScope = PurchaseAssigneeScope.MY_ASSIGNED
)

class PurchaseListViewModel : ViewModel() {
    private val apiService = RetrofitClient.apiService

    private val _uiState = MutableStateFlow(PurchaseListUiState())
    val uiState: StateFlow<PurchaseListUiState> = _uiState.asStateFlow()

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        coerceInputValues = true
    }

    init {
        loadLists()
    }

    fun loadLists() {
        val current = _uiState.value
        if (current.isLoading) return
        _uiState.update { it.copy(isLoading = true, error = null) }
        viewModelScope.launch {
            try {
                val response = apiService.getPurchaseLists(
                    status = _uiState.value.statusFilter.value,
                    assigneeScope = _uiState.value.assigneeScope.value
                )
                if (response.isSuccessful) {
                    val body = response.body()
                    _uiState.update {
                        it.copy(
                            lists = body?.lists ?: emptyList(),
                            isLoading = false
                        )
                    }
                } else {
                    val errorMsg = parseError(
                        response.code(),
                        response.errorBody()?.string()
                    )
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            error = errorMsg
                        )
                    }
                }
            } catch (e: IOException) {
                _uiState.update {
                    it.copy(isLoading = false, error = "网络连接失败，请检查网络")
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = "加载失败：${e.message ?: "未知错误"}"
                    )
                }
            }
        }
    }

    fun setStatusFilter(filter: PurchaseStatusFilter) {
        val current = _uiState.value
        if (current.statusFilter == filter) return
        _uiState.update { it.copy(statusFilter = filter) }
        loadLists()
    }

    fun setAssigneeScope(scope: PurchaseAssigneeScope) {
        val current = _uiState.value
        if (current.assigneeScope == scope) return
        _uiState.update { it.copy(assigneeScope = scope) }
        loadLists()
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
