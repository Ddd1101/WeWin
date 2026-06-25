package com.wewin.app.ui.profile

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Logout
import androidx.compose.material.icons.filled.Business
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.Numbers
import androidx.compose.material.icons.filled.Phone
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.ListItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.wewin.app.data.local.TokenStore
import com.wewin.app.data.remote.dto.UserInfo

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    tokenStore: TokenStore,
    onLogout: () -> Unit
) {
    val user by tokenStore.userFlow.collectAsState(initial = null)

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        UserHeader(user = user)
        InfoCard(user = user)
        Button(
            onClick = onLogout,
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.buttonColors(
                containerColor = MaterialTheme.colorScheme.error,
                contentColor = MaterialTheme.colorScheme.onError
            )
        ) {
            Icon(
                imageVector = Icons.AutoMirrored.Filled.Logout,
                contentDescription = null
            )
            Spacer(Modifier.width(8.dp))
            Text("退出登录")
        }
    }
}

@Composable
private fun UserHeader(user: UserInfo?) {
    val username = user?.username ?: "未登录"
    val initial = username.firstOrNull()?.uppercaseChar()?.toString() ?: "?"
    val realName = user?.real_name
    val typeLabel = userTypeLabel(user?.user_type)

    Card(modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(64.dp)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.primaryContainer),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = initial,
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )
            }
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = username,
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
                if (!realName.isNullOrBlank()) {
                    Spacer(Modifier.height(4.dp))
                    Text(
                        text = realName,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Spacer(Modifier.height(8.dp))
                Surface(
                    color = MaterialTheme.colorScheme.secondaryContainer,
                    contentColor = MaterialTheme.colorScheme.onSecondaryContainer,
                    shape = MaterialTheme.shapes.small
                ) {
                    Text(
                        text = typeLabel,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp),
                        style = MaterialTheme.typography.labelSmall
                    )
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun InfoCard(user: UserInfo?) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column {
            InfoRow(
                icon = Icons.Filled.Business,
                label = "企业",
                value = user?.company_name?.takeIf { it.isNotBlank() } ?: "未绑定企业"
            )
            InfoRow(
                icon = Icons.Filled.Email,
                label = "邮箱",
                value = user?.email?.takeIf { it.isNotBlank() } ?: "未设置"
            )
            InfoRow(
                icon = Icons.Filled.Phone,
                label = "手机",
                value = user?.phone?.takeIf { it.isNotBlank() } ?: "未设置"
            )
            InfoRow(
                icon = Icons.Filled.Numbers,
                label = "用户ID",
                value = user?.id?.toString() ?: "-"
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun InfoRow(
    icon: ImageVector,
    label: String,
    value: String
) {
    ListItem(
        leadingContent = {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        },
        headlineContent = { Text(label) },
        supportingContent = { Text(value) }
    )
}

private fun userTypeLabel(type: String?): String {
    return when (type) {
        "super_admin" -> "超级管理员"
        "site_admin" -> "站点管理员"
        "enterprise_leader" -> "企业负责人"
        "enterprise_admin" -> "企业管理员"
        "enterprise_user" -> "企业用户"
        "temporary" -> "临时用户"
        else -> "未知用户"
    }
}
