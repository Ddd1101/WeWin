package com.wewin.app.ui.purchase

import android.widget.Toast
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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.wewin.app.data.remote.dto.PurchaseItemDto
import com.wewin.app.data.remote.dto.PurchaseListDto

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PurchaseDetailScreen(navController: NavController, listId: Int) {
    val viewModel: PurchaseDetailViewModel = viewModel(
        factory = PurchaseDetailViewModel.factory(listId)
    )
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current

    var partialItemId by remember { mutableStateOf<Int?>(null) }
    var partialInput by remember { mutableStateOf("") }

    LaunchedEffect(uiState.toast) {
        uiState.toast?.let {
            Toast.makeText(context, it, Toast.LENGTH_SHORT).show()
            viewModel.clearToast()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("采购清单详情") },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "返回"
                        )
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
                uiState.isLoading && uiState.list == null -> {
                    CircularProgressIndicator(
                        modifier = Modifier.align(Alignment.Center)
                    )
                }
                uiState.error != null && uiState.list == null -> {
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
                uiState.list == null -> {
                    Text(
                        text = "暂无采购清单信息",
                        modifier = Modifier.align(Alignment.Center),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        style = MaterialTheme.typography.bodyLarge
                    )
                }
                else -> {
                    PurchaseDetailContent(
                        list = uiState.list!!,
                        actionLoading = uiState.actionLoading,
                        onMarkPurchased = viewModel::markPurchased,
                        onMarkPartial = { itemId ->
                            val item = uiState.list!!.items.find { it.id == itemId }
                            partialInput = if (item != null && item.purchasedQuantity > 0) {
                                formatQuantity(item.purchasedQuantity)
                            } else ""
                            partialItemId = itemId
                        },
                        onCarryOver = viewModel::carryOverNextDay
                    )
                }
            }
        }
    }

    uiState.actionError?.let { errorMsg ->
        AlertDialog(
            onDismissRequest = { viewModel.clearActionError() },
            title = { Text("操作失败") },
            text = { Text(errorMsg) },
            confirmButton = {
                TextButton(onClick = { viewModel.clearActionError() }) {
                    Text("确定")
                }
            }
        )
    }

    partialItemId?.let { itemId ->
        AlertDialog(
            onDismissRequest = { partialItemId = null },
            title = { Text("标记已购买部分") },
            text = {
                OutlinedTextField(
                    value = partialInput,
                    onValueChange = { partialInput = it },
                    label = { Text("已购数量") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth()
                )
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        partialInput.toDoubleOrNull()?.let { qty ->
                            viewModel.markPartial(itemId, qty)
                        }
                        partialItemId = null
                    }
                ) {
                    Text("确认")
                }
            },
            dismissButton = {
                TextButton(onClick = { partialItemId = null }) {
                    Text("取消")
                }
            }
        )
    }
}

@Composable
private fun PurchaseDetailContent(
    list: PurchaseListDto,
    actionLoading: Boolean,
    onMarkPurchased: (Int) -> Unit,
    onMarkPartial: (Int) -> Unit,
    onCarryOver: (Int) -> Unit
) {
    LazyColumn(
        contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item { PurchaseListInfoCard(list = list) }

        items(list.items) { item ->
            PurchaseItemCard(
                item = item,
                actionLoading = actionLoading,
                onMarkPurchased = { onMarkPurchased(item.id) },
                onMarkPartial = { onMarkPartial(item.id) },
                onCarryOver = { onCarryOver(item.id) }
            )
        }

        item { Spacer(Modifier.height(16.dp)) }
    }
}

@Composable
private fun PurchaseListInfoCard(list: PurchaseListDto) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = list.title.ifBlank { "未命名清单" },
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface
            )

            PurchaseListStatusChip(status = list.status, display = list.statusDisplay)

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "指派给：${list.assigneeName.ifBlank { "未指派" }}",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.weight(1f)
                )
                if (list.plannedDate.isNotBlank()) {
                    Text(
                        text = list.plannedDate,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            if (list.notes.isNotBlank()) {
                Text(
                    text = list.notes,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "创建人：${list.createdByName.ifBlank { "未知" }}",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                if (list.createdAt.isNotBlank()) {
                    Text(
                        text = list.createdAt.take(10),
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            Spacer(Modifier.height(4.dp))

            val totalCount = list.totalCount.coerceAtLeast(0)
            val purchasedCount = list.purchasedCount.coerceAtLeast(0)
            val progress = if (totalCount > 0) {
                (purchasedCount.toFloat() / totalCount.toFloat()).coerceIn(0f, 1f)
            } else 0f

            Text(
                text = "$purchasedCount/$totalCount 已购买",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface,
                fontWeight = FontWeight.Medium
            )
            LinearProgressIndicator(
                progress = { progress },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(6.dp),
                color = MaterialTheme.colorScheme.primary,
                trackColor = MaterialTheme.colorScheme.surfaceVariant,
                strokeCap = StrokeCap.Round
            )
        }
    }
}

@Composable
private fun PurchaseItemCard(
    item: PurchaseItemDto,
    actionLoading: Boolean,
    onMarkPurchased: () -> Unit,
    onMarkPartial: () -> Unit,
    onCarryOver: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = item.productName.ifBlank { item.skuCode.ifBlank { "未命名商品" } },
                    fontSize = 15.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.onSurface,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.weight(1f)
                )
                PurchaseItemStatusChip(status = item.status, display = item.statusDisplay)
            }

            if (item.skuCode.isNotBlank()) {
                Text(
                    text = "货号：${item.skuCode}",
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            val specParts = buildList {
                if (item.material.isNotBlank()) add(item.material)
                item.size?.let { add(it.toString()) }
                if (item.color.isNotBlank()) add(item.color)
            }
            if (specParts.isNotEmpty()) {
                Text(
                    text = specParts.joinToString(" · "),
                    fontSize = 13.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "数量：${formatQuantity(item.quantity)}${item.unit}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    text = "单价：¥${"%.2f".format(item.unitPrice)}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurface
                )
            }

            val hasSupplier = item.supplier.isNotBlank()
            val hasLocation = item.location.isNotBlank()
            if (hasSupplier || hasLocation) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = if (hasSupplier) "供应商：${item.supplier}" else "",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                        modifier = Modifier.weight(1f)
                    )
                    if (hasLocation) {
                        Text(
                            text = "库位：${item.location}",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }

            item.qualityLevel?.let { quality ->
                Text(
                    text = "品质：$quality/10",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            if (item.status != "pending" && item.purchasedQuantity > 0) {
                Text(
                    text = "已购：${formatQuantity(item.purchasedQuantity)}${item.unit}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.primary,
                    fontWeight = FontWeight.Medium
                )
            }

            if (item.remark.isNotBlank()) {
                Text(
                    text = "备注：${item.remark}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            if (item.status != "purchased") {
                Spacer(Modifier.height(4.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    OutlinedButton(
                        onClick = onMarkPurchased,
                        enabled = !actionLoading,
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("已购买", maxLines = 1)
                    }
                    OutlinedButton(
                        onClick = onMarkPartial,
                        enabled = !actionLoading,
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("已购买部分", maxLines = 1)
                    }
                    OutlinedButton(
                        onClick = onCarryOver,
                        enabled = !actionLoading,
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("添加到下一日", maxLines = 1)
                    }
                    if (actionLoading) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(20.dp),
                            strokeWidth = 2.dp
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun PurchaseListStatusChip(status: String, display: String) {
    val containerColor: Color
    val contentColor: Color
    when (status) {
        "pending" -> {
            containerColor = MaterialTheme.colorScheme.surfaceVariant
            contentColor = MaterialTheme.colorScheme.onSurfaceVariant
        }
        "in_progress" -> {
            containerColor = MaterialTheme.colorScheme.primaryContainer
            contentColor = MaterialTheme.colorScheme.onPrimaryContainer
        }
        "completed" -> {
            containerColor = MaterialTheme.colorScheme.tertiaryContainer
            contentColor = MaterialTheme.colorScheme.onTertiaryContainer
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
            text = display.ifBlank { status },
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 3.dp),
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
private fun PurchaseItemStatusChip(status: String, display: String) {
    val containerColor: Color
    val contentColor: Color
    when (status) {
        "pending" -> {
            containerColor = MaterialTheme.colorScheme.surfaceVariant
            contentColor = MaterialTheme.colorScheme.onSurfaceVariant
        }
        "partially_purchased" -> {
            containerColor = MaterialTheme.colorScheme.primaryContainer
            contentColor = MaterialTheme.colorScheme.onPrimaryContainer
        }
        "purchased" -> {
            containerColor = MaterialTheme.colorScheme.tertiaryContainer
            contentColor = MaterialTheme.colorScheme.onTertiaryContainer
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
            text = display.ifBlank { status },
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp),
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.Medium
        )
    }
}

private fun formatQuantity(value: Double): String {
    return if (value == value.toLong().toDouble()) {
        value.toLong().toString()
    } else {
        value.toString()
    }
}
