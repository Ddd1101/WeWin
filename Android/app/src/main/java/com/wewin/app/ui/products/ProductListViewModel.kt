package com.wewin.app.ui.products

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.wewin.app.data.remote.RetrofitClient
import com.wewin.app.data.remote.dto.ErrorResponse
import com.wewin.app.data.remote.dto.ProductDto
import com.wewin.app.data.remote.dto.ProductStatsDto.ProductStats
import com.wewin.app.data.remote.dto.SkuDto
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.Job
import kotlinx.coroutines.CancellationException
import kotlinx.serialization.json.Json
import java.io.IOException

sealed interface SkuLoadState {
    object Idle : SkuLoadState
    object Loading : SkuLoadState
    data class Success(val skus: List<SkuDto>) : SkuLoadState
    data class Error(val message: String) : SkuLoadState
}

data class ProductListUiState(
    val products: List<ProductDto> = emptyList(),
    val stats: ProductStats? = null,
    val isLoading: Boolean = false,
    val isLoadingMore: Boolean = false,
    val error: String? = null,
    val selectedType: String? = null,
    val searchKeyword: String = "",
    val page: Int = 1,
    val totalCount: Int = 0,
    val hasMore: Boolean = true,
    val isRefreshing: Boolean = false,
    val skuMap: Map<Int, SkuLoadState> = emptyMap()
)

class ProductListViewModel : ViewModel() {

    private val apiService = RetrofitClient.apiService

    private val pageSize: Int = 50
    private var generation = 0L
    private var activeKeyword: String? = null
    private var initialJob: Job? = null
    private var moreJob: Job? = null

    private val _uiState = MutableStateFlow(ProductListUiState())
    val uiState: StateFlow<ProductListUiState> = _uiState.asStateFlow()

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        coerceInputValues = true
    }

    init {
        loadInitial()
    }

    fun loadInitial() {
        val request = _uiState.value
        val ticket = ++generation
        activeKeyword = request.searchKeyword.trim().ifBlank { null }
        initialJob?.cancel()
        moreJob?.cancel()
        _uiState.update { it.copy(isLoading = true, isLoadingMore = false, error = null, page = 1,
            hasMore = false, products = emptyList(), skuMap = emptyMap()) }
        initialJob = viewModelScope.launch {
            try {
                coroutineScope {
                    val list = async { apiService.getProducts(productType = request.selectedType, page = 1,
                        pageSize = pageSize, search = request.searchKeyword.trim().ifBlank { null }) }
                    val stats = async { apiService.getProductStats() }
                    val response = list.await()
                    val statistics = stats.await()
                    if (ticket != generation) return@coroutineScope
                    if (response.isSuccessful) {
                        val body = response.body()
                        val products = body?.products.orEmpty()
                        val total = body?.total_count ?: 0
                        _uiState.update { it.copy(products = products, totalCount = total, page = 1,
                            hasMore = products.size < total, stats = if (statistics.isSuccessful) statistics.body()?.product_stats else it.stats,
                            isLoading = false, isRefreshing = false, error = null) }
                    } else {
                        _uiState.update { it.copy(isLoading = false, isRefreshing = false,
                            error = parseError(response.code(), response.errorBody()?.string())) }
                    }
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                if (ticket == generation) _uiState.update { it.copy(isLoading = false, isRefreshing = false,
                    error = if (e is IOException) "网络连接失败，请检查网络" else "加载失败：${e.message ?: "未知错误"}") }
            }
        }
    }

    fun loadMore() {
        val request = _uiState.value
        if (request.isLoading || request.isLoadingMore || !request.hasMore) return
        val ticket = generation
        val keyword = activeKeyword
        _uiState.update { it.copy(isLoadingMore = true) }
        moreJob = viewModelScope.launch {
            try {
                val response = apiService.getProducts(productType = request.selectedType, page = request.page + 1,
                    pageSize = pageSize, search = keyword)
                if (ticket != generation) return@launch
                if (response.isSuccessful) {
                    val body = response.body()
                    val products = (request.products + body?.products.orEmpty()).distinctBy { it.id }
                    val total = body?.total_count ?: request.totalCount
                    _uiState.update { it.copy(products = products, totalCount = total, page = request.page + 1,
                        hasMore = products.size < total, isLoadingMore = false, error = null) }
                } else {
                    _uiState.update { it.copy(isLoadingMore = false, error = parseError(response.code(), response.errorBody()?.string())) }
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                if (ticket == generation) _uiState.update { it.copy(isLoadingMore = false,
                    error = if (e is IOException) "网络连接失败，请检查网络" else "加载失败：${e.message ?: "未知错误"}") }
            }
        }
    }

    fun refresh() {
        _uiState.update { it.copy(isRefreshing = true) }
        loadInitial()
    }

    fun selectType(type: String?) {
        if (_uiState.value.selectedType == type) return
        _uiState.update { it.copy(selectedType = type) }
        loadInitial()
    }

    fun updateKeyword(keyword: String) {
        _uiState.update { it.copy(searchKeyword = keyword) }
    }

    fun search() = loadInitial()

    fun loadSkusIfNeeded(productId: Int, existingSkus: List<SkuDto>) {
        if (existingSkus.isNotEmpty()) {
            val current = _uiState.value.skuMap[productId]
            if (current !is SkuLoadState.Success) {
                _uiState.update {
                    it.copy(skuMap = it.skuMap + (productId to SkuLoadState.Success(existingSkus)))
                }
            }
            return
        }
        val state = _uiState.value.skuMap[productId]
        if (state is SkuLoadState.Loading || state is SkuLoadState.Success) return
        _uiState.update {
            it.copy(skuMap = it.skuMap + (productId to SkuLoadState.Loading))
        }
        val ticket = generation
        viewModelScope.launch {
            try {
                val response = apiService.getProductSkus(productId)
                if (ticket != generation) return@launch
                if (response.isSuccessful) {
                    val skus = response.body()?.skus ?: emptyList()
                    _uiState.update {
                        it.copy(skuMap = it.skuMap + (productId to SkuLoadState.Success(skus)))
                    }
                } else {
                    val errorMsg = parseError(
                        response.code(),
                        response.errorBody()?.string()
                    )
                    _uiState.update {
                        it.copy(skuMap = it.skuMap + (productId to SkuLoadState.Error(errorMsg)))
                    }
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: IOException) {
                if (ticket != generation) return@launch
                _uiState.update {
                    it.copy(skuMap = it.skuMap + (productId to SkuLoadState.Error("网络连接失败，请检查网络")))
                }
            } catch (e: Exception) {
                if (ticket != generation) return@launch
                _uiState.update {
                    it.copy(skuMap = it.skuMap + (productId to SkuLoadState.Error("加载失败：${e.message ?: "未知错误"}")))
                }
            }
        }
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

    private fun httpErrorMessage(code: Int): String {
        return when (code) {
            401 -> "未授权，请重新登录"
            403 -> "没有访问权限"
            404 -> "接口不存在"
            in 500..599 -> "服务器错误，请稍后重试"
            else -> "请求失败（$code）"
        }
    }
}
