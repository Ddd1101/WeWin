package com.wewin.app.ui.products

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Image
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.KeyboardArrowUp
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import com.wewin.app.data.remote.dto.ProductDto
import com.wewin.app.data.remote.dto.ProductStatsDto.ProductStats
import com.wewin.app.data.remote.dto.SkuDto

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProductListScreen(
    onNavigateToProductDetail: (Int) -> Unit,
    onNavigateToProductEdit: (Int?) -> Unit,
    viewModel: ProductListViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("商品管理") },
                actions = {
                    IconButton(onClick = { viewModel.refresh() }) {
                        Icon(
                            imageVector = Icons.Filled.Refresh,
                            contentDescription = "刷新"
                        )
                    }
                }
            )
        },
        floatingActionButton = {
            FloatingActionButton(onClick = { onNavigateToProductEdit(null) }) {
                Icon(
                    imageVector = Icons.Filled.Add,
                    contentDescription = "新建商品"
                )
            }
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            StatsCards(stats = uiState.stats)

            TypeFilterChips(
                selectedType = uiState.selectedType,
                onSelect = viewModel::selectType
            )

            SearchField(
                keyword = uiState.searchKeyword,
                onKeywordChange = viewModel::updateKeyword,
                onSearch = viewModel::search
            )

            val keyword = uiState.searchKeyword.trim()
            val filteredProducts = remember(uiState.products, keyword) {
                if (keyword.isEmpty()) {
                    uiState.products
                } else {
                    uiState.products.filter { product ->
                        product.code.contains(keyword, ignoreCase = true) ||
                            product.name.contains(keyword, ignoreCase = true)
                    }
                }
            }

            ProductListContent(
                uiState = uiState,
                filteredProducts = filteredProducts,
                onProductClick = onNavigateToProductDetail,
                onRetry = viewModel::loadInitial,
                onLoadMore = viewModel::loadMore,
                onLoadSkus = viewModel::loadSkusIfNeeded,
                onRetryLoadSkus = viewModel::loadSkusIfNeeded
            )
        }
    }
}

@Composable
private fun ProductListContent(
    uiState: ProductListUiState,
    filteredProducts: List<ProductDto>,
    onProductClick: (Int) -> Unit,
    onRetry: () -> Unit,
    onLoadMore: () -> Unit,
    onLoadSkus: (Int, List<SkuDto>) -> Unit,
    onRetryLoadSkus: (Int, List<SkuDto>) -> Unit
) {
    val listState = rememberLazyListState()
    var expandedIds by remember { mutableStateOf<Set<Int>>(emptySet()) }

    val shouldLoadMore by remember {
        derivedStateOf {
            val layoutInfo = listState.layoutInfo
            val totalItems = layoutInfo.totalItemsCount
            val lastVisibleIndex = layoutInfo.visibleItemsInfo.lastOrNull()?.index ?: 0
            totalItems > 0 && lastVisibleIndex >= totalItems - 3
        }
    }

    LaunchedEffect(shouldLoadMore, uiState.page) {
        if (shouldLoadMore) {
            onLoadMore()
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        when {
            uiState.isLoading && uiState.products.isEmpty() -> {
                CircularProgressIndicator(
                    modifier = Modifier.align(Alignment.Center)
                )
            }
            uiState.error != null && uiState.products.isEmpty() -> {
                Column(
                    modifier = Modifier.align(Alignment.Center),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = uiState.error,
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodyMedium
                    )
                    Spacer(Modifier.height(8.dp))
                    Button(onClick = onRetry) {
                        Text("重试")
                    }
                }
            }
            filteredProducts.isEmpty() && !uiState.isLoading -> {
                Text(
                    text = "暂无商品",
                    modifier = Modifier.align(Alignment.Center),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    style = MaterialTheme.typography.bodyLarge
                )
            }
            else -> {
                LazyColumn(
                    state = listState,
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(filteredProducts) { product ->
                        val isExpanded = expandedIds.contains(product.id)
                        ProductCard(
                            product = product,
                            onClick = { onProductClick(product.id) },
                            isExpanded = isExpanded,
                            onToggleExpand = {
                                expandedIds = if (isExpanded) {
                                    expandedIds - product.id
                                } else {
                                    expandedIds + product.id
                                }
                                if (!isExpanded) {
                                    onLoadSkus(product.id, product.skus)
                                }
                            },
                            skuLoadState = uiState.skuMap[product.id],
                            onRetryLoadSkus = { onRetryLoadSkus(product.id, product.skus) }
                        )
                    }
                    if (uiState.isLoadingMore) {
                        item {
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(16.dp),
                                contentAlignment = Alignment.Center
                            ) {
                                CircularProgressIndicator()
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun StatsCards(stats: ProductStats?) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .horizontalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 8.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        StatCard(
            label = "总数",
            count = stats?.total_count ?: 0,
            color = MaterialTheme.colorScheme.primary
        )
        StatCard(
            label = "启用",
            count = stats?.active_count ?: 0,
            color = MaterialTheme.colorScheme.tertiary
        )
        StatCard(
            label = "串珠",
            count = stats?.bead_count ?: 0,
            color = MaterialTheme.colorScheme.primary
        )
        StatCard(
            label = "配件",
            count = stats?.accessory_count ?: 0,
            color = MaterialTheme.colorScheme.tertiary
        )
        StatCard(
            label = "成品",
            count = stats?.finished_count ?: 0,
            color = MaterialTheme.colorScheme.secondary
        )
    }
}

@Composable
private fun StatCard(label: String, count: Int, color: Color) {
    Card(
        modifier = Modifier.width(96.dp),
        colors = CardDefaults.cardColors(
            containerColor = color.copy(alpha = 0.12f)
        )
    ) {
        Column(
            modifier = Modifier
                .padding(vertical = 12.dp, horizontal = 8.dp)
                .fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = count.toString(),
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = color
            )
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun TypeFilterChips(
    selectedType: String?,
    onSelect: (String?) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .horizontalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 4.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        val chips = listOf(
            null to "全部",
            "bead" to "串珠",
            "accessory" to "配件",
            "finished" to "成品"
        )
        chips.forEach { (type, label) ->
            FilterChip(
                selected = selectedType == type,
                onClick = { onSelect(type) },
                label = { Text(label) }
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SearchField(
    keyword: String,
    onKeywordChange: (String) -> Unit,
    onSearch: () -> Unit
) {
    OutlinedTextField(
        value = keyword,
        onValueChange = onKeywordChange,
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 4.dp),
        placeholder = { Text("搜索货号或名称") },
        leadingIcon = {
            Icon(
                imageVector = Icons.Filled.Search,
                contentDescription = null
            )
        },
        trailingIcon = {
            IconButton(onClick = onSearch) {
                Icon(
                    imageVector = Icons.Filled.Search,
                    contentDescription = "搜索"
                )
            }
        },
        singleLine = true,
        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
        keyboardActions = KeyboardActions(onSearch = { onSearch() })
    )
}

@Composable
private fun ProductCard(
    product: ProductDto,
    onClick: () -> Unit,
    isExpanded: Boolean = false,
    onToggleExpand: () -> Unit = {},
    skuLoadState: SkuLoadState? = null,
    onRetryLoadSkus: () -> Unit = {}
) {
    if (product.product_type == "bead") {
        Card(modifier = Modifier.fillMaxWidth()) {
            Column {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onToggleExpand() }
                        .padding(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    ProductThumbnail(imageUrl = product.image_url)

                    Spacer(Modifier.width(12.dp))

                    Column(modifier = Modifier.weight(1f)) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Text(
                                text = product.code,
                                style = MaterialTheme.typography.titleSmall,
                                fontWeight = FontWeight.Bold
                            )
                            TypeChip(
                                productType = product.product_type,
                                display = product.product_type_display
                            )
                            Spacer(Modifier.weight(1f))
                            if (!product.is_active) {
                                Surface(
                                    color = MaterialTheme.colorScheme.surfaceVariant,
                                    contentColor = MaterialTheme.colorScheme.onSurfaceVariant,
                                    shape = RoundedCornerShape(50)
                                ) {
                                    Text(
                                        text = "已停用",
                                        modifier = Modifier.padding(
                                            horizontal = 6.dp,
                                            vertical = 1.dp
                                        ),
                                        style = MaterialTheme.typography.labelSmall
                                    )
                                }
                            }
                            IconButton(
                                onClick = onClick,
                                modifier = Modifier.size(28.dp)
                            ) {
                                Icon(
                                    imageVector = Icons.Filled.Info,
                                    contentDescription = "详情",
                                    modifier = Modifier.size(18.dp)
                                )
                            }
                            Icon(
                                imageVector = if (isExpanded) {
                                    Icons.Filled.KeyboardArrowUp
                                } else {
                                    Icons.Filled.KeyboardArrowDown
                                },
                                contentDescription = if (isExpanded) "收起" else "展开"
                            )
                        }

                        Spacer(Modifier.height(4.dp))

                        Text(
                            text = product.name,
                            style = MaterialTheme.typography.bodyMedium,
                            maxLines = 2,
                            overflow = TextOverflow.Ellipsis
                        )

                        Spacer(Modifier.height(4.dp))
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Text(
                                text = "成本 ¥${"%.2f".format(product.cost_price)}",
                                color = MaterialTheme.colorScheme.onSurface,
                                fontWeight = FontWeight.SemiBold,
                                style = MaterialTheme.typography.titleSmall
                            )
                            Text(
                                text = "售价 ¥${"%.2f".format(product.selling_price)}",
                                color = MaterialTheme.colorScheme.error,
                                fontWeight = FontWeight.Bold,
                                style = MaterialTheme.typography.titleSmall
                            )
                        }
                    }
                }

                if (isExpanded) {
                    HorizontalDivider(
                        color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f)
                    )
                    Column(modifier = Modifier.padding(12.dp)) {
                        when (skuLoadState) {
                            null, is SkuLoadState.Idle -> {}
                            is SkuLoadState.Loading -> {
                                Box(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(8.dp),
                                    contentAlignment = Alignment.Center
                                ) {
                                    CircularProgressIndicator(modifier = Modifier.size(24.dp))
                                }
                            }
                            is SkuLoadState.Error -> {
                                Column(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalAlignment = Alignment.CenterHorizontally
                                ) {
                                    Text(
                                        text = skuLoadState.message,
                                        color = MaterialTheme.colorScheme.error,
                                        style = MaterialTheme.typography.bodySmall
                                    )
                                    Spacer(Modifier.height(4.dp))
                                    Button(onClick = onRetryLoadSkus) {
                                        Text("重试")
                                    }
                                }
                            }
                            is SkuLoadState.Success -> {
                                if (skuLoadState.skus.isEmpty()) {
                                    Text(
                                        text = "暂无 SKU",
                                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                                        style = MaterialTheme.typography.bodySmall
                                    )
                                } else {
                                    Column {
                                        skuLoadState.skus.forEachIndexed { index, sku ->
                                            SkuRow(sku = sku)
                                            if (index < skuLoadState.skus.lastIndex) {
                                                HorizontalDivider(
                                                    color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f)
                                                )
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    } else {
        Card(
            onClick = onClick,
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier.padding(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                ProductThumbnail(imageUrl = product.image_url)

                Spacer(Modifier.width(12.dp))

                Column(modifier = Modifier.weight(1f)) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = product.code,
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold
                        )
                        TypeChip(
                            productType = product.product_type,
                            display = product.product_type_display
                        )
                        Spacer(Modifier.weight(1f))
                        if (!product.is_active) {
                            Surface(
                                color = MaterialTheme.colorScheme.surfaceVariant,
                                contentColor = MaterialTheme.colorScheme.onSurfaceVariant,
                                shape = RoundedCornerShape(50)
                            ) {
                                Text(
                                    text = "已停用",
                                    modifier = Modifier.padding(
                                        horizontal = 6.dp,
                                        vertical = 1.dp
                                    ),
                                    style = MaterialTheme.typography.labelSmall
                                )
                            }
                        }
                    }

                    Spacer(Modifier.height(4.dp))

                    Text(
                        text = product.name,
                        style = MaterialTheme.typography.bodyMedium,
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis
                    )

                    if (product.product_type == "finished") {
                        val profit = product.selling_price - product.cost_price
                        val rate = if (product.selling_price > 0) {
                            (profit / product.selling_price) * 100
                        } else null

                        // Thin horizontal divider above metrics (replaces the spacer)
                        HorizontalDivider(
                            color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f),
                            modifier = Modifier.padding(top = 2.dp, bottom = 4.dp)
                        )

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(0.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            MetricColumn(
                                label = "成本",
                                value = "¥${"%.2f".format(product.cost_price)}",
                                valueColor = MaterialTheme.colorScheme.onSurface,
                                modifier = Modifier.weight(1f)
                            )
                            Box(
                                modifier = Modifier
                                    .width(1.dp)
                                    .height(28.dp)
                                    .background(MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f))
                            )
                            MetricColumn(
                                label = "售价",
                                value = "¥${"%.2f".format(product.selling_price)}",
                                valueColor = MaterialTheme.colorScheme.error,
                                modifier = Modifier
                                    .weight(1f)
                                    .padding(horizontal = 6.dp)
                            )
                            Box(
                                modifier = Modifier
                                    .width(1.dp)
                                    .height(28.dp)
                                    .background(MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f))
                            )
                            MetricColumn(
                                label = "利润",
                                value = "¥${"%.2f".format(profit)}",
                                valueColor = if (profit >= 0) Color(0xFF10B981) else MaterialTheme.colorScheme.error,
                                modifier = Modifier
                                    .weight(1f)
                                    .padding(horizontal = 6.dp)
                            )
                            Box(
                                modifier = Modifier
                                    .width(1.dp)
                                    .height(28.dp)
                                    .background(MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f))
                            )
                            MetricColumn(
                                label = "利润率",
                                value = if (rate != null) "${"%.1f".format(rate)}%" else "-",
                                valueColor = when {
                                    rate == null -> MaterialTheme.colorScheme.onSurface
                                    rate >= 30 -> Color(0xFF10B981)
                                    rate >= 15 -> Color(0xFFF59E0B)
                                    else -> MaterialTheme.colorScheme.error
                                },
                                modifier = Modifier.weight(1f)
                            )
                        }
                    } else {
                        Spacer(Modifier.height(4.dp))
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Text(
                                text = "成本 ¥${"%.2f".format(product.cost_price)}",
                                color = MaterialTheme.colorScheme.onSurface,
                                fontWeight = FontWeight.SemiBold,
                                style = MaterialTheme.typography.titleSmall
                            )
                            Text(
                                text = "售价 ¥${"%.2f".format(product.selling_price)}",
                                color = MaterialTheme.colorScheme.error,
                                fontWeight = FontWeight.Bold,
                                style = MaterialTheme.typography.titleSmall
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun SkuRow(sku: SkuDto) {
    val title = sku.sku_code?.takeIf { it.isNotBlank() }
        ?: sku.name?.takeIf { it.isNotBlank() }
        ?: sku.sku_name
        ?: "SKU ${sku.id}"

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 6.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.bodySmall,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.weight(1f)
            )
            if (sku.is_default) {
                Surface(
                    color = MaterialTheme.colorScheme.primaryContainer,
                    contentColor = MaterialTheme.colorScheme.onPrimaryContainer,
                    shape = RoundedCornerShape(50)
                ) {
                    Text(
                        text = "默认",
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 1.dp),
                        style = MaterialTheme.typography.labelSmall
                    )
                }
            }
            if (!sku.is_active) {
                Surface(
                    color = MaterialTheme.colorScheme.surfaceVariant,
                    contentColor = MaterialTheme.colorScheme.onSurfaceVariant,
                    shape = RoundedCornerShape(50)
                ) {
                    Text(
                        text = "已停用",
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 1.dp),
                        style = MaterialTheme.typography.labelSmall
                    )
                }
            }
        }

        Spacer(Modifier.height(4.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            MetricColumn(
                label = "规格",
                value = sku.size?.toString() ?: "-",
                valueColor = MaterialTheme.colorScheme.onSurface,
                modifier = Modifier.weight(1f)
            )
            MetricColumn(
                label = "颜色",
                value = sku.color ?: "-",
                valueColor = MaterialTheme.colorScheme.onSurface,
                modifier = Modifier.weight(1f)
            )
            MetricColumn(
                label = "克重",
                value = "%.2f".format(sku.weight),
                valueColor = MaterialTheme.colorScheme.onSurface,
                modifier = Modifier.weight(1f)
            )
            MetricColumn(
                label = "采购成本",
                value = "¥${"%.2f".format(sku.purchase_cost)}",
                valueColor = MaterialTheme.colorScheme.onSurface,
                modifier = Modifier.weight(1f)
            )
        }

        Spacer(Modifier.height(2.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            MetricColumn(
                label = "成本价",
                value = "¥${"%.2f".format(sku.cost_price)}",
                valueColor = MaterialTheme.colorScheme.onSurface,
                modifier = Modifier.weight(1f)
            )
            MetricColumn(
                label = "售价",
                value = "¥${"%.2f".format(sku.selling_price)}",
                valueColor = MaterialTheme.colorScheme.error,
                modifier = Modifier.weight(1f)
            )
            MetricColumn(
                label = "品质",
                value = sku.quality_level.toString(),
                valueColor = MaterialTheme.colorScheme.onSurface,
                modifier = Modifier.weight(1f)
            )
            MetricColumn(
                label = "库位",
                value = sku.location ?: "-",
                valueColor = MaterialTheme.colorScheme.onSurface,
                modifier = Modifier.weight(1f)
            )
        }

        Spacer(Modifier.height(2.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            MetricColumn(
                label = "供应商",
                value = sku.supplier ?: "-",
                valueColor = MaterialTheme.colorScheme.onSurface,
                modifier = Modifier.weight(1f)
            )
            MetricColumn(
                label = "备注",
                value = sku.remark ?: "-",
                valueColor = MaterialTheme.colorScheme.onSurface,
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
private fun MetricColumn(
    label: String,
    value: String,
    valueColor: Color,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier,
        horizontalAlignment = Alignment.Start
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.6f)
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodySmall,
            fontWeight = FontWeight.SemiBold,
            color = valueColor
        )
    }
}

@Composable
private fun ProductThumbnail(imageUrl: String?) {
    val shape = RoundedCornerShape(8.dp)
    if (!imageUrl.isNullOrBlank()) {
        AsyncImage(
            model = imageUrl,
            contentDescription = null,
            modifier = Modifier
                .size(80.dp)
                .clip(shape),
            contentScale = ContentScale.Crop
        )
    } else {
        Box(
            modifier = Modifier
                .size(80.dp)
                .clip(shape)
                .background(MaterialTheme.colorScheme.surfaceVariant),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = Icons.Filled.Image,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun TypeChip(productType: String, display: String?) {
    val containerColor: Color
    val contentColor: Color
    when (productType) {
        "bead" -> {
            containerColor = MaterialTheme.colorScheme.primaryContainer
            contentColor = MaterialTheme.colorScheme.onPrimaryContainer
        }
        "accessory" -> {
            containerColor = MaterialTheme.colorScheme.tertiaryContainer
            contentColor = MaterialTheme.colorScheme.onTertiaryContainer
        }
        "finished" -> {
            containerColor = MaterialTheme.colorScheme.secondaryContainer
            contentColor = MaterialTheme.colorScheme.onSecondaryContainer
        }
        else -> {
            containerColor = MaterialTheme.colorScheme.surfaceVariant
            contentColor = MaterialTheme.colorScheme.onSurfaceVariant
        }
    }
    Surface(
        color = containerColor,
        contentColor = contentColor,
        shape = RoundedCornerShape(50)
    ) {
        Text(
            text = display ?: productType,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp),
            style = MaterialTheme.typography.labelSmall
        )
    }
}
