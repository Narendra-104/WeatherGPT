package com.weathergpt.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.weathergpt.app.R
import com.weathergpt.app.data.model.*
import com.weathergpt.app.ui.theme.*
import com.weathergpt.app.ui.viewmodel.UiState
import com.weathergpt.app.ui.viewmodel.WeatherViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    viewModel: WeatherViewModel,
    onNavigateToChat: () -> Unit,
    modifier: Modifier = Modifier
) {
    val currentCity by viewModel.currentCity.collectAsState()
    val language by viewModel.language.collectAsState()
    val weatherState by viewModel.weatherState.collectAsState()
    val forecastState by viewModel.forecastState.collectAsState()
    val alertsState by viewModel.alertsState.collectAsState()

    var searchQuery by remember { mutableStateOf("") }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .background(DarkBackground)
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Spacer(modifier = Modifier.height(8.dp))
            // Search Bar & Language Switcher
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                OutlinedTextField(
                    value = searchQuery,
                    onValueChange = { searchQuery = it },
                    placeholder = { Text(stringResource(R.string.search_hint), color = TextSecondary, fontSize = 14.sp) },
                    modifier = Modifier.weight(1f),
                    singleLine = true,
                    shape = RoundedCornerShape(14.dp),
                    trailingIcon = {
                        IconButton(onClick = {
                            if (searchQuery.isNotBlank()) {
                                viewModel.searchCity(searchQuery)
                                searchQuery = ""
                            }
                        }) {
                            Icon(Icons.Default.Search, contentDescription = "Search", tint = Blue80)
                        }
                    },
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedContainerColor = DarkSurface,
                        unfocusedContainerColor = DarkSurface,
                        focusedTextColor = TextPrimary,
                        unfocusedTextColor = TextPrimary,
                        cursorColor = Blue80,
                        focusedBorderColor = Blue80,
                        unfocusedBorderColor = DarkSurfaceVariant
                    )
                )

                // Language selector pills
                Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                    listOf("en" to "EN", "hi" to "हि", "mr" to "म").forEach { (code, label) ->
                        FilterChip(
                            selected = language == code,
                            onClick = { viewModel.setLanguage(code) },
                            label = { Text(label, fontSize = 12.sp, fontWeight = FontWeight.Bold) },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = Blue80,
                                selectedLabelColor = DarkBackground,
                                containerColor = DarkSurface,
                                labelColor = TextSecondary
                            )
                        )
                    }
                }
            }
        }

        // Severe Alerts Banner
        if (alertsState is UiState.Success) {
            val alerts = (alertsState as UiState.Success<List<WeatherAlert>>).data
            if (alerts.isNotEmpty()) {
                item {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        alerts.forEach { alert ->
                            AlertCard(alert)
                        }
                    }
                }
            }
        }

        // Current Weather Hero Card
        item {
            when (val state = weatherState) {
                is UiState.Loading -> {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(200.dp)
                            .clip(RoundedCornerShape(20.dp))
                            .background(DarkSurface),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator(color = Blue80)
                    }
                }
                is UiState.Error -> {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = DarkSurface),
                        shape = RoundedCornerShape(20.dp)
                    ) {
                        Column(
                            modifier = Modifier.padding(24.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text(text = state.message, color = AlertRed, fontSize = 15.sp)
                            Spacer(modifier = Modifier.height(12.dp))
                            Button(
                                onClick = { viewModel.loadWeatherData() },
                                colors = ButtonDefaults.buttonColors(containerColor = Blue80)
                            ) {
                                Text(stringResource(R.string.retry), color = DarkBackground)
                            }
                        }
                    }
                }
                is UiState.Success -> {
                    HeroWeatherCard(weather = state.data)
                }
                UiState.Idle -> {}
            }
        }

        // Metrics Grid
        if (weatherState is UiState.Success) {
            val weather = (weatherState as UiState.Success<CurrentWeather>).data
            item {
                MetricsSection(weather)
            }
        }

        // Hourly Forecast
        if (forecastState is UiState.Success) {
            val forecast = (forecastState as UiState.Success<ForecastResponse>).data
            if (forecast.hourly.isNotEmpty()) {
                item {
                    Text(
                        text = stringResource(R.string.hourly_forecast),
                        style = MaterialTheme.typography.titleLarge,
                        color = TextPrimary
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    HourlyForecastRow(forecast.hourly)
                }
            }

            // Daily Forecast
            if (forecast.daily.isNotEmpty()) {
                item {
                    Text(
                        text = stringResource(R.string.daily_forecast),
                        style = MaterialTheme.typography.titleLarge,
                        color = TextPrimary
                    )
                }
                items(forecast.daily) { day ->
                    DailyForecastCard(day)
                }
            }
        }

        item {
            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}

@Composable
fun HeroWeatherCard(weather: CurrentWeather) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(24.dp))
            .background(
                Brush.verticalGradient(
                    colors = listOf(Color(0xFF0369A1), Color(0xFF0F172A))
                )
            )
            .padding(24.dp)
    ) {
        Column {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column {
                    Text(
                        text = weather.location.name,
                        style = MaterialTheme.typography.titleLarge,
                        color = TextPrimary,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = weather.location.country ?: "",
                        style = MaterialTheme.typography.bodyLarge,
                        color = TextSecondary
                    )
                }
                Icon(
                    imageVector = Icons.Default.WbSunny,
                    contentDescription = null,
                    tint = AlertAmber,
                    modifier = Modifier.size(48.dp)
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            Text(
                text = "${weather.temperatureC.toInt()}°C",
                fontSize = 64.sp,
                fontWeight = FontWeight.ExtraBold,
                color = TextPrimary
            )

            Text(
                text = weather.weatherDescription,
                fontSize = 18.sp,
                fontWeight = FontWeight.SemiBold,
                color = Cyan80
            )

            Spacer(modifier = Modifier.height(6.dp))

            Text(
                text = "${stringResource(R.string.feels_like)} ${weather.feelsLikeC.toInt()}°C",
                fontSize = 14.sp,
                color = TextSecondary
            )
        }
    }
}

@Composable
fun MetricsSection(weather: CurrentWeather) {
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            MetricCard(
                icon = Icons.Default.WaterDrop,
                title = stringResource(R.string.humidity),
                value = "${weather.humidityPercent}%",
                modifier = Modifier.weight(1f)
            )
            MetricCard(
                icon = Icons.Default.Air,
                title = stringResource(R.string.wind_speed),
                value = "${weather.windSpeedKmh} km/h",
                modifier = Modifier.weight(1f)
            )
        }
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            MetricCard(
                icon = Icons.Default.Umbrella,
                title = stringResource(R.string.precipitation),
                value = "${weather.precipitationMm} mm",
                modifier = Modifier.weight(1f)
            )
            MetricCard(
                icon = Icons.Default.Speed,
                title = stringResource(R.string.pressure),
                value = "${weather.pressureHpa?.toInt() ?: "--"} hPa",
                modifier = Modifier.weight(1f)
            )
        }
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            MetricCard(
                icon = Icons.Default.WbSunny,
                title = stringResource(R.string.uv_index),
                value = weather.uvIndex?.toString() ?: "--",
                modifier = Modifier.weight(1f)
            )
            MetricCard(
                icon = Icons.Default.Schedule,
                title = stringResource(R.string.sunrise),
                value = weather.sunrise ?: "--:--",
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
fun MetricCard(
    icon: ImageVector,
    title: String,
    value: String,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = DarkSurface),
        shape = RoundedCornerShape(16.dp)
    ) {
        Row(
            modifier = Modifier.padding(14.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .background(DarkSurfaceVariant),
                contentAlignment = Alignment.Center
            ) {
                Icon(icon, contentDescription = null, tint = Blue80, modifier = Modifier.size(22.dp))
            }
            Column {
                Text(title, fontSize = 12.sp, color = TextSecondary)
                Text(value, fontSize = 15.sp, fontWeight = FontWeight.Bold, color = TextPrimary)
            }
        }
    }
}

@Composable
fun HourlyForecastRow(hourly: List<HourlyPoint>) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .horizontalScroll(rememberScrollState()),
        horizontalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        hourly.take(24).forEach { point ->
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkSurface),
                shape = RoundedCornerShape(16.dp)
            ) {
                Column(
                    modifier = Modifier.padding(12.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = point.time.substringAfter("T").take(5),
                        fontSize = 12.sp,
                        color = TextSecondary
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    Icon(
                        Icons.Default.Cloud,
                        contentDescription = null,
                        tint = Blue80,
                        modifier = Modifier.size(24.dp)
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = "${point.temperatureC.toInt()}°",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary
                    )
                }
            }
        }
    }
}

@Composable
fun DailyForecastCard(day: DailyForecast) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        colors = CardDefaults.cardColors(containerColor = DarkSurface),
        shape = RoundedCornerShape(14.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                text = day.date,
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium,
                color = TextPrimary,
                modifier = Modifier.width(100.dp)
            )

            Text(
                text = day.weatherDescription,
                fontSize = 13.sp,
                color = TextSecondary,
                modifier = Modifier.weight(1f)
            )

            Text(
                text = "${day.minTempC.toInt()}° / ${day.maxTempC.toInt()}°",
                fontSize = 14.sp,
                fontWeight = FontWeight.Bold,
                color = Cyan80
            )
        }
    }
}

@Composable
fun AlertCard(alert: WeatherAlert) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (alert.severity.equals("extreme", true)) Color(0xFF450A0A) else Color(0xFF451A03)
        ),
        shape = RoundedCornerShape(16.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.Top,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Icon(
                Icons.Default.Warning,
                contentDescription = null,
                tint = if (alert.severity.equals("extreme", true)) AlertRed else AlertAmber,
                modifier = Modifier.size(28.dp)
            )
            Column {
                Text(alert.headline, fontWeight = FontWeight.Bold, color = TextPrimary, fontSize = 14.sp)
                Spacer(modifier = Modifier.height(4.dp))
                Text(alert.description, color = TextSecondary, fontSize = 12.sp)
                if (!alert.instruction.isNullOrBlank()) {
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = alert.instruction,
                        color = AlertAmber,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold
                    )
                }
            }
        }
    }
}
