package com.weathergpt.app.data.model

import com.google.gson.annotations.SerializedName

data class ApiResponse<T>(
    @SerializedName("success") val success: Boolean,
    @SerializedName("data") val data: T?,
    @SerializedName("error") val error: ApiError?,
    @SerializedName("provider") val provider: String?,
    @SerializedName("cached") val cached: Boolean = false
)

data class ApiError(
    @SerializedName("code") val code: String,
    @SerializedName("message") val message: String,
    @SerializedName("details") val details: Any? = null
)

data class LocationInfo(
    @SerializedName("name") val name: String,
    @SerializedName("latitude") val latitude: Double,
    @SerializedName("longitude") val longitude: Double,
    @SerializedName("country") val country: String? = null,
    @SerializedName("admin1") val admin1: String? = null
)

data class CurrentWeather(
    @SerializedName("location") val location: LocationInfo,
    @SerializedName("temperature_c") val temperatureC: Double,
    @SerializedName("feels_like_c") val feelsLikeC: Double,
    @SerializedName("humidity_percent") val humidityPercent: Int,
    @SerializedName("wind_speed_kmh") val windSpeedKmh: Double,
    @SerializedName("wind_direction_deg") val windDirectionDeg: Int? = null,
    @SerializedName("precipitation_mm") val precipitationMm: Double = 0.0,
    @SerializedName("pressure_hpa") val pressureHpa: Double? = null,
    @SerializedName("uv_index") val uvIndex: Double? = null,
    @SerializedName("weather_code") val weatherCode: Int? = null,
    @SerializedName("weather_description") val weatherDescription: String,
    @SerializedName("is_day") val isDay: Boolean = true,
    @SerializedName("sunrise") val sunrise: String? = null,
    @SerializedName("sunset") val sunset: String? = null,
    @SerializedName("timestamp") val timestamp: String
)

data class HourlyPoint(
    @SerializedName("time") val time: String,
    @SerializedName("temperature_c") val temperatureC: Double,
    @SerializedName("weather_description") val weatherDescription: String,
    @SerializedName("precipitation_probability") val precipitationProbability: Int = 0,
    @SerializedName("wind_speed_kmh") val windSpeedKmh: Double = 0.0
)

data class DailyForecast(
    @SerializedName("date") val date: String,
    @SerializedName("min_temp_c") val minTempC: Double,
    @SerializedName("max_temp_c") val maxTempC: Double,
    @SerializedName("weather_description") val weatherDescription: String,
    @SerializedName("precipitation_probability") val precipitationProbability: Int = 0,
    @SerializedName("precipitation_mm") val precipitationMm: Double = 0.0,
    @SerializedName("sunrise") val sunrise: String? = null,
    @SerializedName("sunset") val sunset: String? = null
)

data class ForecastResponse(
    @SerializedName("location") val location: LocationInfo,
    @SerializedName("current") val current: CurrentWeather?,
    @SerializedName("hourly") val hourly: List<HourlyPoint> = emptyList(),
    @SerializedName("daily") val daily: List<DailyForecast> = emptyList()
)

data class WeatherAlert(
    @SerializedName("id") val id: String,
    @SerializedName("event") val event: String,
    @SerializedName("severity") val severity: String,
    @SerializedName("urgency") val urgency: String? = null,
    @SerializedName("headline") val headline: String,
    @SerializedName("description") val description: String,
    @SerializedName("instruction") val instruction: String? = null,
    @SerializedName("source") val source: String,
    @SerializedName("effective") val effective: String? = null,
    @SerializedName("expires") val expires: String? = null
)

data class AlertsResponse(
    @SerializedName("location") val location: String,
    @SerializedName("alerts") val alerts: List<WeatherAlert> = emptyList(),
    @SerializedName("count") val count: Int = 0
)

data class ChatMessage(
    @SerializedName("role") val role: String,
    @SerializedName("content") val content: String,
    @SerializedName("timestamp") val timestamp: String? = null
)

data class ChatRequest(
    @SerializedName("message") val message: String,
    @SerializedName("location") val location: String? = null,
    @SerializedName("language") val language: String = "en",
    @SerializedName("conversation_history") val conversationHistory: List<ChatMessage> = emptyList()
)

data class GroundedData(
    @SerializedName("location") val location: String? = null,
    @SerializedName("temperature_c") val temperatureC: Double? = null,
    @SerializedName("description") val description: String? = null,
    @SerializedName("forecast_summary") val forecastSummary: String? = null
)

data class ChatResponse(
    @SerializedName("reply") val reply: String,
    @SerializedName("language") val language: String,
    @SerializedName("grounded_data") val groundedData: GroundedData? = null
)
