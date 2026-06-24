package com.wewin.app.ui.products

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Image
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import com.wewin.app.data.remote.dto.AccessoryDto
import com.wewin.app.data.remote.dto.BeadDto
import com.wewin.app.data.remote.dto.FinishedAccessoryItemDto
import com.wewin.app.data.remote.dto.FinishedBeadItemDto
import com.wewin.app.data.remote.dto.FinishedDto
import com.wewin.app.data.remote.dto.ProductDto
import com.wewin.app.data.remote.dto.SkuDto

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProductDetailScreen(
    productId: Int,
    onBack: () -> Unit,
    onEdit: (Int) -> Unit,
    viewModel: ProductDetailViewModel = viewModel(
        factory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T =
                ProductDetailViewModel(productId) as T
        }
    )
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("商品详情") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "返回"
                        )
                    }
                },
                actions = {
                    val product = uiState.product
                    if (product != null) {
                        IconButton(onClick = { onEdit(product.id) }) {
                            Icon(
                                imageVector = Icons.Filled.Edit,
                                contentDescription = "编辑"
                            )
                        }
                    }
                }
            )
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            when {
                uiState.isLoading -> {
                    CircularProgressIndicator(
                        modifier = Modifier.align(Alignment.Center)
                    )
                }
                uiState.error != null && uiState.product == null -> {
                    Column(
                        modifier = Modifier.align(Alignment.Center),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = uiState.error ?: "未知错误",
                            color = MaterialTheme.colorScheme.error,
                            style = MaterialTheme.typography.bodyMedium
                        )
                        Spacer(Modifier.height(8.dp))
                        Button(onClick = { viewModel.loadDetail() }) {
                            Text("重试")
                        }
                    }
                }
                uiState.product == null -> {
                    Text(
                        text = "暂无商品信息",
                        modifier = Modifier.align(Alignment.Center),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        style = MaterialTheme.typography.bodyLarge
                    )
                }
                else -> {
                    ProductDetailContent(
                        product = uiState.product!!,
                        error = uiState.error
                    )
                }
            }
        }
    }
}

@Composable
private fun ProductDetailContent(
    product: ProductDto,
    error: String?
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(
            horizontal = 16.dp,
            vertical = 8.dp
        ),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item { ProductImage(imageUrl = product.image_url) }

        if (product.product_type == "finished") {
            item { PriceHeroCard(product = product) }
        }

        item { BasicInfoCard(product = product) }

        product.bead?.let { bead ->
            item { BeadInfoCard(bead = bead) }
        }

        product.accessory?.let { accessory ->
            item { AccessoryInfoCard(accessory = accessory) }
        }

        product.finished?.let { finished ->
            item { FinishedInfoCard(finished = finished) }
        }

        if (product.skus.isNotEmpty()) {
            item { SkuListCard(skus = product.skus) }
        }

        if (error != null) {
            item {
                Surface(
                    color = MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.6f),
                    shape = RoundedCornerShape(8.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = error,
                        modifier = Modifier.padding(12.dp),
                        color = MaterialTheme.colorScheme.onErrorContainer,
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
        }

        item { Spacer(Modifier.height(16.dp)) }
    }
}

@Composable
private fun ProductImage(imageUrl: String?) {
    val shape = RoundedCornerShape(12.dp)
    if (!imageUrl.isNullOrBlank()) {
        AsyncImage(
            model = imageUrl,
            contentDescription = "商品图片",
            modifier = Modifier
                .fillMaxWidth()
                .aspectRatio(1f)
                .clip(shape),
            contentScale = ContentScale.Crop
        )
    } else {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .aspectRatio(1f)
                .clip(shape)
                .background(MaterialTheme.colorScheme.surfaceVariant),
            contentAlignment = Alignment.Center
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Icon(
                    imageVector = Icons.Filled.Image,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.size(48.dp)
                )
                Spacer(Modifier.height(8.dp))
                Text(
                    text = "暂无图片",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }
    }
}

@Composable
private fun PriceHeroCard(product: ProductDto) {
    val profit = product.selling_price - product.cost_price
    val rate = if (product.selling_price > 0) {
        (profit / product.selling_price) * 100
    } else null

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
    ) {
        Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                MetricItem(
                    label = "成本",
                    value = "¥${"%.2f".format(product.cost_price)}",
                    valueColor = MaterialTheme.colorScheme.onSurface,
                    modifier = Modifier.weight(1f)
                )
                MetricItem(
                    label = "售价",
                    value = "¥${"%.2f".format(product.selling_price)}",
                    valueColor = MaterialTheme.colorScheme.error,
                    valueWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f)
                )
            }
            Spacer(Modifier.height(12.dp))
            HorizontalDivider()
            Spacer(Modifier.height(12.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                MetricItem(
                    label = "利润",
                    value = "¥${"%.2f".format(profit)}",
                    valueColor = if (profit >= 0) Color(0xFF10B981) else MaterialTheme.colorScheme.error,
                    modifier = Modifier.weight(1f)
                )
                MetricItem(
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
        }
    }
}

@Composable
private fun MetricItem(
    label: String,
    value: String,
    valueColor: Color,
    modifier: Modifier = Modifier,
    valueWeight: FontWeight = FontWeight.SemiBold
) {
    Column(modifier = modifier) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.6f)
        )
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = valueWeight,
            color = valueColor
        )
    }
}

@Composable
private fun BasicInfoCard(product: ProductDto) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = product.code,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f)
                )
                TypeChip(
                    productType = product.product_type,
                    display = product.product_type_display
                )
            }

            ActiveStatusChip(isActive = product.is_active)

            HorizontalDivider()

            InfoRow(label = "商品名称", value = product.name)
            if (product.product_type != "finished") {
                InfoRow(
                    label = "采购成本",
                    value = "¥${"%.2f".format(product.purchase_cost)} /克"
                )
                InfoRow(
                    label = "单颗成本",
                    value = "¥${"%.2f".format(product.cost_price)}"
                )
                InfoRow(
                    label = "售价",
                    value = "¥${"%.2f".format(product.selling_price)}",
                    valueColor = MaterialTheme.colorScheme.error,
                    valueWeight = FontWeight.Bold
                )
            }
            InfoRow(label = "库位", value = product.location)
            InfoRow(label = "供应商", value = product.supplier)
            InfoRow(label = "所属企业", value = product.company_name)
            InfoRow(label = "创建人", value = product.created_by_name)
            InfoRow(label = "创建时间", value = product.created_at?.take(19))
        }
    }
}

@Composable
private fun ActiveStatusChip(isActive: Boolean) {
    val containerColor: Color
    val contentColor: Color
    val text: String
    if (isActive) {
        containerColor = Color(0xFFE8F5E9)
        contentColor = Color(0xFF2E7D32)
        text = "启用"
    } else {
        containerColor = Color(0xFFFFEBEE)
        contentColor = Color(0xFFC62828)
        text = "已停用"
    }
    Surface(
        color = containerColor,
        contentColor = contentColor,
        shape = RoundedCornerShape(50)
    ) {
        Text(
            text = text,
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 3.dp),
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
private fun BeadInfoCard(bead: BeadDto) {
    DetailCard(title = "串珠参数") {
        InfoRow(label = "材质", value = bead.material)
        InfoRow(label = "规格", value = bead.size?.toString())
        InfoRow(label = "颜色", value = bead.color)
        InfoRow(
            label = "单颗克重",
            value = "${"%.2f".format(bead.weight)} 克"
        )
        InfoRow(label = "品质等级", value = bead.quality_level.toString())
        InfoRow(label = "备注", value = bead.remark)
    }
}

@Composable
private fun AccessoryInfoCard(accessory: AccessoryDto) {
    DetailCard(title = "配件参数") {
        InfoRow(label = "材质", value = accessory.material)
        InfoRow(label = "规格", value = accessory.size?.toString())
        InfoRow(label = "颜色", value = accessory.color)
    }
}

@Composable
private fun FinishedInfoCard(finished: FinishedDto) {
    DetailCard(title = "成品组成") {
        InfoRow(
            label = "工费",
            value = "¥${"%.2f".format(finished.labor_cost)}"
        )
        InfoRow(
            label = "弹性成本",
            value = "¥${"%.2f".format(finished.elastic_cost)}"
        )

        if (finished.beads.isNotEmpty()) {
            Spacer(Modifier.height(8.dp))
            Text(
                text = "串珠组成",
                style = MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.Bold
            )
            Spacer(Modifier.height(4.dp))
            finished.beads.forEach { item ->
                FinishedBeadItemRow(item = item)
                Spacer(Modifier.height(4.dp))
            }
        }

        if (finished.accessories.isNotEmpty()) {
            Spacer(Modifier.height(8.dp))
            Text(
                text = "配件组成",
                style = MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.Bold
            )
            Spacer(Modifier.height(4.dp))
            finished.accessories.forEach { item ->
                FinishedAccessoryItemRow(item = item)
                Spacer(Modifier.height(4.dp))
            }
        }
    }
}

@Composable
private fun FinishedBeadItemRow(item: FinishedBeadItemDto) {
    Surface(
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f),
        shape = RoundedCornerShape(10.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(12.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Left accent: quantity badge
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    text = "x${item.quantity}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )
            }

            // Right: name + details
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = item.bead_name ?: "未命名",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Bold
                )
                item.bead_code?.let {
                    Text(
                        text = "货号 $it",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
                    )
                }
                // Price row: 3 items with labels above values
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    CompactMetric(
                        label = "克价",
                        value = item.bead_purchase_cost?.let { "¥${"%.2f".format(it)}/g" } ?: "-",
                        modifier = Modifier.weight(1f)
                    )
                    CompactMetric(
                        label = "单价",
                        value = "¥${"%.2f".format(item.bead_cost_price)}",
                        modifier = Modifier.weight(1f)
                    )
                    CompactMetric(
                        label = "小计",
                        value = "¥${"%.2f".format(item.bead_cost_price * item.quantity)}",
                        modifier = Modifier.weight(1f)
                    )
                }
                item.sku?.let { sku ->
                    Text(
                        text = "SKU：${sku.sku_code ?: "-"}",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
                    )
                }
            }
        }
    }
}

@Composable
private fun CompactMetric(
    label: String,
    value: String,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.6f)
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodySmall,
            fontWeight = FontWeight.SemiBold,
            color = MaterialTheme.colorScheme.onSurface
        )
    }
}

@Composable
private fun FinishedAccessoryItemRow(item: FinishedAccessoryItemDto) {
    Surface(
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f),
        shape = RoundedCornerShape(10.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(12.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    text = "x${item.quantity}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )
            }
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = item.accessory_name ?: "未命名",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Bold
                )
                item.accessory_code?.let {
                    Text(
                        text = "货号 $it",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
                    )
                }
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    CompactMetric(
                        label = "成本",
                        value = "¥${"%.2f".format(item.accessory_cost_price)}",
                        modifier = Modifier.weight(1f)
                    )
                    item.sku?.let { sku ->
                        CompactMetric(
                            label = "SKU",
                            value = sku.sku_code ?: "-",
                            modifier = Modifier.weight(1f)
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun SkuListCard(skus: List<SkuDto>) {
    DetailCard(title = "SKU 列表") {
        skus.forEach { sku ->
            SkuItemRow(sku = sku)
            Spacer(Modifier.height(8.dp))
        }
    }
}

@Composable
private fun SkuItemRow(sku: SkuDto) {
    Surface(
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f),
        shape = RoundedCornerShape(8.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(10.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = sku.sku_code ?: sku.name ?: "未命名",
                    style = MaterialTheme.typography.bodyMedium,
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
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp),
                            style = MaterialTheme.typography.labelSmall
                        )
                    }
                }
            }

            val specParts = buildList {
                sku.material?.let { add(it) }
                sku.size?.let { add("${it}mm") }
                sku.color?.let { add(it) }
            }
            if (specParts.isNotEmpty()) {
                Text(
                    text = specParts.joinToString(" / "),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text(
                    text = "克重：${"%.2f".format(sku.weight)}g",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = "品质：${sku.quality_level}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text(
                    text = "成本：¥${"%.2f".format(sku.cost_price)}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = "售价：¥${"%.2f".format(sku.selling_price)}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.error,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}

@Composable
private fun DetailCard(
    title: String,
    content: @Composable () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )
            HorizontalDivider()
            content()
        }
    }
}

@Composable
private fun InfoRow(
    label: String,
    value: String?,
    valueColor: Color = MaterialTheme.colorScheme.onSurface,
    valueWeight: FontWeight = FontWeight.Normal
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.width(88.dp)
        )
        Text(
            text = value?.takeIf { it.isNotBlank() } ?: "-",
            style = MaterialTheme.typography.bodyMedium,
            color = valueColor,
            fontWeight = valueWeight
        )
    }
}

@Composable
private fun HorizontalDivider() {
    androidx.compose.material3.HorizontalDivider(
        color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f)
    )
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
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 3.dp),
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.Bold
        )
    }
}
