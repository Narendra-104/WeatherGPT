package com.weathergpt.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CompareArrows
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.weathergpt.app.R
import com.weathergpt.app.data.model.CurrentWeather
import com.weathergpt.app.ui.theme.*
import com.weathergpt.app.ui.viewmodel.WeatherViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CompareScreen(
    viewModel: WeatherViewModel,
    modifier: Modifier = Modifier
) {
    val compareState by viewModel.compareState.collectAsState()

    var inputCity1 by remember { mutableStateOf(compareState.city1) }
    var inputCity2 by remember { mutableStateOf(compareState.city2) }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(DarkBackground)
            .padding(16.dp)
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = stringResource(R.string.compare_cities),
            style = MaterialTheme.typography.titleLarge,
            color = TextPrimary
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            OutlinedTextField(
                value = inputCity1,
                onValueChange = { inputCity1 = it },
                label = { Text("City 1", fontSize = 12.sp) },
                modifier = Modifier.weight(1f),
                singleLine = true,
                shape = RoundedCornerShape(12.dp),
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

            OutlinedTextField(
                value = inputCity2,
                onValueChange = { inputCity2 = it },
                label = { Text("City 2", fontSize = 12.sp) },
                modifier = Modifier.weight(1f),
                singleLine = true,
                shape = RoundedCornerShape(12.dp),
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
        }

        Button(
            onClick = {
                viewModel.compareCities(inputCity1, inputCity2)
            },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            colors = ButtonDefaults.buttonColors(containerColor = Blue80)
        ) {
            Icon(Icons.Default.CompareArrows, contentDescription = null, tint = DarkBackground)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Compare Real-Time Weather", color = DarkBackground, fontWeight = FontWeight.Bold)
        }

        if (compareState.isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(180.dp),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(color = Blue80)
            }
        } else if (compareState.errorMessage != null) {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkSurface),
                shape = RoundedCornerShape(14.dp)
            ) {
                Text(
                    text = compareState.errorMessage ?: "",
                    color = AlertRed,
                    modifier = Modifier.padding(16.dp),
                    fontSize = 14.sp
                )
            }
        } else if (compareState.weather1 != null && compareState.weather2 != null) {
            ComparisonTable(w1 = compareState.weather1!!, w2 = compareState.weather2!!)
        }
    }
}

@Composable
fun ComparisonTable(w1: CurrentWeather, w2: CurrentWeather) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = DarkSurface),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            // Header Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("Metric", fontWeight = FontWeight.Bold, color = TextSecondary, modifier = Modifier.weight(1.2f))
                Text(w1.location.name, fontWeight = FontWeight.Bold, color = Blue80, modifier = Modifier.weight(1f))
                Text(w2.location.name, fontWeight = FontWeight.Bold, color = Cyan80, modifier = Modifier.weight(1f))
            }
            Divider(color = DarkSurfaceVariant, modifier = Modifier.padding(vertical = 10.dp))

            ComparisonRow("Temperature", "${w1.temperatureC.toInt()}°C", "${w2.temperatureC.toInt()}°C")
            ComparisonRow("Feels Like", "${w1.feelsLikeC.toInt()}°C", "${w2.feelsLikeC.toInt()}°C")
            ComparisonRow("Condition", w1.weatherDescription, w2.weatherDescription)
            ComparisonRow("Humidity", "${w1.humidityPercent}%", "${w2.humidityPercent}%")
            ComparisonRow("Wind", "${w1.windSpeedKmh} km/h", "${w2.windSpeedKmh} km/h")
            ComparisonRow("Pressure", "${w1.pressureHpa?.toInt() ?: "--"} hPa", "${w2.pressureHpa?.toInt() ?: "--"} hPa")
            ComparisonRow("Precipitation", "${w1.precipitationMm} mm", "${w2.precipitationMm} mm")
        }
    }
}

@Composable
fun ComparisonRow(metric: String, val1: String, val2: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 6.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(metric, fontSize = 13.sp, color = TextSecondary, modifier = Modifier.weight(1.2f))
        Text(val1, fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = TextPrimary, modifier = Modifier.weight(1f))
        Text(val2, fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = TextPrimary, modifier = Modifier.weight(1f))
    }
}
