package com.wewin.app.ui.purchase

import android.app.DatePickerDialog
import android.widget.Toast
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CalendarMonth
import androidx.compose.material.icons.filled.ExpandMore
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.runtime.collectAsState
import com.wewin.app.data.remote.dto.CreatePurchaseItemRequest
import com.wewin.app.data.remote.dto.PurchaseListSummaryDto
import com.wewin.app.data.remote.dto.UserBriefDto
import java.util.Calendar
import java.util.GregorianCalendar
import java.util.Locale
import java.text.SimpleDateFormat

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AddToPurchaseSheet(
    prefill: PurchasePrefillData,
    onDismiss: () -> Unit
) {
    val viewModel: AddToPurchaseViewModel = viewModel()
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current

    // 默认计划日期 = 明天，格式 YYYY-MM-DD
    val tomorrow = remember {
        val cal = Calendar.getInstance()
        cal.add(Calendar.DAY_OF_MONTH, 1)
        SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(cal.time)
    }

    // 表单状态
    var mode by remember { mutableStateOf("new") } // "new" / "existing"
    var title by remember { mutableStateOf("采购清单 $tomorrow") }
    var selectedAssigneeId by remember { mutableStateOf<Int?>(null) }
    var plannedDate by remember { mutableStateOf(tomorrow) }
    var notes by remember { mutableStateOf("") }
    var selectedListId by remember { mutableStateOf<Int?>(null) }
    var quantity by remember {
        mutableStateOf(if (prefill.defaultUnit == "克") "10" else "1")
    }
    var unit by remember { mutableStateOf(prefill.defaultUnit) }
    var unitPrice by remember { mutableStateOf(prefill.defaultUnitPrice.toString()) }
    var remark by remember { mutableStateOf("") }

    // 加载选项
    LaunchedEffect(Unit) { viewModel.loadOptions() }

    // 成功后关闭
    LaunchedEffect(uiState.success) {
        if (uiState.success) {
            Toast.makeText(context, "已加入采购清单", Toast.LENGTH_SHORT).show()
            onDismiss()
        }
    }

    // 错误提示
    LaunchedEffect(uiState.error) {
        uiState.error?.let {
            Toast.makeText(context, it, Toast.LENGTH_SHORT).show()
            viewModel.clearError()
        }
    }

    ModalBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 8.dp)
                .imePadding()
                .verticalScroll(rememberScrollState())
        ) {
            // 标题
            Text(
                "加入采购清单",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
            Spacer(Modifier.height(8.dp))

            // 预填信息展示（只读卡片）
            PrefillInfoCard(prefill)

            Spacer(Modifier.height(12.dp))

            // 模式切换：新建清单 / 加入已有清单
            Row {
                FilterChip(
                    selected = mode == "new",
                    onClick = { mode = "new" },
                    label = { Text("新建清单") }
                )
                Spacer(Modifier.width(8.dp))
                FilterChip(
                    selected = mode == "existing",
                    onClick = { mode = "existing" },
                    label = { Text("加入已有") }
                )
            }

            Spacer(Modifier.height(12.dp))

            if (mode == "new") {
                // 新建清单表单
                OutlinedTextField(
                    value = title,
                    onValueChange = { title = it },
                    label = { Text("清单标题") },
                    modifier = Modifier.fillMaxWidth()
                )
                Spacer(Modifier.height(8.dp))

                // 指派人选择器（下拉）
                AssigneeSelector(
                    users = uiState.users,
                    selectedId = selectedAssigneeId,
                    onSelect = { selectedAssigneeId = it }
                )
                Spacer(Modifier.height(8.dp))

                // 计划日期
                DateField(
                    label = "计划日期",
                    date = plannedDate,
                    onDateChange = { plannedDate = it }
                )
                Spacer(Modifier.height(8.dp))

                OutlinedTextField(
                    value = notes,
                    onValueChange = { notes = it },
                    label = { Text("备注（可选）") },
                    modifier = Modifier.fillMaxWidth()
                )
                Spacer(Modifier.height(12.dp))
            } else {
                // 加入已有清单：下拉选择
                ExistingListSelector(
                    lists = uiState.uncompletedLists,
                    selectedId = selectedListId,
                    onSelect = { selectedListId = it }
                )
                Spacer(Modifier.height(12.dp))
            }

            // 采购项录入（数量/单位/单价/备注）
            Text(
                "采购项信息",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold
            )
            Spacer(Modifier.height(8.dp))

            Row {
                OutlinedTextField(
                    value = quantity,
                    onValueChange = { quantity = it.filter { c -> c.isDigit() || c == '.' } },
                    label = { Text("数量") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    modifier = Modifier.weight(1f)
                )
                Spacer(Modifier.width(8.dp))
                OutlinedTextField(
                    value = unit,
                    onValueChange = { unit = it },
                    label = { Text("单位") },
                    modifier = Modifier.weight(1f)
                )
            }
            Spacer(Modifier.height(8.dp))

            OutlinedTextField(
                value = unitPrice,
                onValueChange = { unitPrice = it.filter { c -> c.isDigit() || c == '.' } },
                label = { Text("单价（元）") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(Modifier.height(8.dp))

            OutlinedTextField(
                value = remark,
                onValueChange = { remark = it },
                label = { Text("备注（可选）") },
                modifier = Modifier.fillMaxWidth()
            )

            Spacer(Modifier.height(16.dp))

            // 提交按钮
            Button(
                onClick = {
                    val item = CreatePurchaseItemRequest(
                        productId = prefill.productId,
                        skuId = prefill.skuId,
                        productType = prefill.productType,
                        productName = prefill.productName,
                        skuCode = prefill.skuCode,
                        quantity = quantity.toDoubleOrNull() ?: 0.0,
                        unit = unit,
                        unitPrice = unitPrice.toDoubleOrNull() ?: 0.0,
                        supplier = prefill.supplier,
                        location = prefill.location,
                        qualityLevel = prefill.qualityLevel,
                        material = prefill.material,
                        size = prefill.size,
                        color = prefill.color,
                        remark = remark
                    )
                    if (mode == "new") {
                        if (selectedAssigneeId == null) {
                            Toast.makeText(context, "请选择指派人", Toast.LENGTH_SHORT).show()
                            return@Button
                        }
                        viewModel.createNewListAndAddItem(
                            title,
                            selectedAssigneeId!!,
                            plannedDate,
                            notes,
                            item
                        )
                    } else {
                        if (selectedListId == null) {
                            Toast.makeText(context, "请选择清单", Toast.LENGTH_SHORT).show()
                            return@Button
                        }
                        viewModel.addItemToExistingList(selectedListId!!, item)
                    }
                },
                enabled = !uiState.isSubmitting,
                modifier = Modifier.fillMaxWidth()
            ) {
                if (uiState.isSubmitting) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(20.dp),
                        strokeWidth = 2.dp
                    )
                } else {
                    Text("提交")
                }
            }
            Spacer(Modifier.height(16.dp))
        }
    }
}

@Composable
private fun PrefillInfoCard(prefill: PurchasePrefillData) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(Modifier.padding(12.dp)) {
            Text(
                prefill.productName,
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.SemiBold
            )
            if (prefill.skuCode.isNotBlank()) {
                Text(
                    "SKU: ${prefill.skuCode}",
                    style = MaterialTheme.typography.bodySmall
                )
            }
            Row {
                Text(
                    "类型: ${if (prefill.productType == "bead") "串珠" else "配件"}",
                    style = MaterialTheme.typography.bodySmall
                )
                Spacer(Modifier.width(12.dp))
                Text(
                    "默认单价: ¥${prefill.defaultUnitPrice}",
                    style = MaterialTheme.typography.bodySmall
                )
            }
            if (prefill.supplier.isNotBlank() || prefill.location.isNotBlank()) {
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    if (prefill.supplier.isNotBlank()) {
                        Text(
                            "供应商: ${prefill.supplier}",
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                    if (prefill.location.isNotBlank()) {
                        Text(
                            "库位: ${prefill.location}",
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun AssigneeSelector(
    users: List<UserBriefDto>,
    selectedId: Int?,
    onSelect: (Int) -> Unit
) {
    var expanded by remember { mutableStateOf(false) }
    val selectedUser = users.find { it.id == selectedId }
    val displayText = selectedUser?.let {
        val name = it.realName.ifBlank { it.username }
        if (it.userTypeDisplay.isNotBlank()) "$name（${it.userTypeDisplay}）" else name
    } ?: ""

    Box(modifier = Modifier.fillMaxWidth()) {
        OutlinedTextField(
            value = displayText,
            onValueChange = {},
            readOnly = true,
            label = { Text("指派人") },
            placeholder = { Text("请选择指派人") },
            trailingIcon = {
                Icon(Icons.Filled.ExpandMore, contentDescription = null)
            },
            modifier = Modifier
                .fillMaxWidth()
                .clickable { expanded = true }
        )
        DropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false }
        ) {
            if (users.isEmpty()) {
                DropdownMenuItem(
                    text = { Text("暂无可指派人员") },
                    onClick = { expanded = false }
                )
            } else {
                users.forEach { user ->
                    val name = user.realName.ifBlank { user.username }
                    val label = if (user.userTypeDisplay.isNotBlank()) {
                        "$name（${user.userTypeDisplay}）"
                    } else {
                        name
                    }
                    DropdownMenuItem(
                        text = { Text(label) },
                        onClick = {
                            onSelect(user.id)
                            expanded = false
                        }
                    )
                }
            }
        }
    }
}

@Composable
private fun ExistingListSelector(
    lists: List<PurchaseListSummaryDto>,
    selectedId: Int?,
    onSelect: (Int) -> Unit
) {
    var expanded by remember { mutableStateOf(false) }
    val selectedList = lists.find { it.id == selectedId }
    val displayText = selectedList?.let {
        val parts = mutableListOf<String>()
        if (it.title.isNotBlank()) parts.add(it.title)
        if (it.plannedDate.isNotBlank()) parts.add(it.plannedDate)
        if (it.statusDisplay.isNotBlank()) parts.add(it.statusDisplay)
        parts.joinToString("，")
    } ?: ""

    Box(modifier = Modifier.fillMaxWidth()) {
        OutlinedTextField(
            value = displayText,
            onValueChange = {},
            readOnly = true,
            label = { Text("选择采购清单") },
            placeholder = { Text("请选择清单") },
            trailingIcon = {
                Icon(Icons.Filled.ExpandMore, contentDescription = null)
            },
            modifier = Modifier
                .fillMaxWidth()
                .clickable { expanded = true }
        )
        DropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false }
        ) {
            if (lists.isEmpty()) {
                DropdownMenuItem(
                    text = { Text("暂无未完成清单") },
                    onClick = { expanded = false }
                )
            } else {
                lists.forEach { list ->
                    val parts = mutableListOf<String>()
                    if (list.title.isNotBlank()) parts.add(list.title)
                    if (list.plannedDate.isNotBlank()) parts.add(list.plannedDate)
                    if (list.statusDisplay.isNotBlank()) parts.add(list.statusDisplay)
                    DropdownMenuItem(
                        text = { Text(parts.joinToString("，")) },
                        onClick = {
                            onSelect(list.id)
                            expanded = false
                        }
                    )
                }
            }
        }
    }
}

@Composable
private fun DateField(
    label: String,
    date: String,
    onDateChange: (String) -> Unit
) {
    val context = LocalContext.current
    val initial = remember(date) {
        try {
            val parts = date.split("-")
            GregorianCalendar(parts[0].toInt(), parts[1].toInt() - 1, parts[2].toInt())
        } catch (e: Exception) {
            GregorianCalendar()
        }
    }
    OutlinedTextField(
        value = date,
        onValueChange = {},
        readOnly = true,
        label = { Text(label) },
        modifier = Modifier
            .fillMaxWidth()
            .clickable {
                DatePickerDialog(
                    context,
                    { _, y, m, d -> onDateChange("%04d-%02d-%02d".format(y, m + 1, d)) },
                    initial.get(Calendar.YEAR),
                    initial.get(Calendar.MONTH),
                    initial.get(Calendar.DAY_OF_MONTH)
                ).show()
            },
        trailingIcon = { Icon(Icons.Filled.CalendarMonth, contentDescription = null) }
    )
}
