package com.weathergpt.app.data.repository

import com.weathergpt.app.data.api.ApiClient
import com.weathergpt.app.data.model.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class WeatherRepository {
    private val api = ApiClient.apiService

    suspend fun getCurrentWeather(city: String? = null, lat: Double? = null, lon: Double? = null, lang: String = "en"): Result<CurrentWeather> =
        withContext(Dispatchers.IO) {
            try {
                val response = api.getCurrentWeather(city, lat, lon, lang)
                if (response.isSuccessful && response.body()?.success == true && response.body()?.data != null) {
                    Result.success(response.body()!!.data!!)
                } else {
                    val errorMsg = response.body()?.error?.message ?: response.message() ?: "Failed to fetch weather"
                    Result.failure(Exception(errorMsg))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }

    suspend fun getForecast(city: String? = null, lat: Double? = null, lon: Double? = null, days: Int = 7, lang: String = "en"): Result<ForecastResponse> =
        withContext(Dispatchers.IO) {
            try {
                val response = api.getForecast(city, lat, lon, days, lang)
                if (response.isSuccessful && response.body()?.success == true && response.body()?.data != null) {
                    Result.success(response.body()!!.data!!)
                } else {
                    val errorMsg = response.body()?.error?.message ?: response.message() ?: "Failed to fetch forecast"
                    Result.failure(Exception(errorMsg))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }

    suspend fun getAlerts(city: String? = null, lat: Double? = null, lon: Double? = null, lang: String = "en"): Result<AlertsResponse> =
        withContext(Dispatchers.IO) {
            try {
                val response = api.getAlerts(city, lat, lon, lang)
                if (response.isSuccessful && response.body()?.success == true && response.body()?.data != null) {
                    Result.success(response.body()!!.data!!)
                } else {
                    val errorMsg = response.body()?.error?.message ?: response.message() ?: "Failed to fetch alerts"
                    Result.failure(Exception(errorMsg))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }

    suspend fun searchLocations(query: String): Result<List<LocationInfo>> =
        withContext(Dispatchers.IO) {
            try {
                val response = api.searchLocations(query)
                if (response.isSuccessful && response.body()?.success == true && response.body()?.data != null) {
                    Result.success(response.body()!!.data!!)
                } else {
                    Result.failure(Exception(response.body()?.error?.message ?: "Location search failed"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }

    suspend fun sendChatMessage(request: ChatRequest): Result<ChatResponse> =
        withContext(Dispatchers.IO) {
            try {
                val response = api.sendChatMessage(request)
                if (response.isSuccessful && response.body()?.success == true && response.body()?.data != null) {
                    Result.success(response.body()!!.data!!)
                } else {
                    val errorMsg = response.body()?.error?.message ?: "AI assistant unavailable"
                    Result.failure(Exception(errorMsg))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
}
