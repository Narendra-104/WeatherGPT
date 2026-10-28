package com.weathergpt.app.data.api

import com.weathergpt.app.data.model.*
import retrofit2.Response
import retrofit2.http.*

interface WeatherApiService {

    @GET("api/v1/health")
    suspend fun checkHealth(): Response<ApiResponse<Map<String, Any>>>

    @GET("api/v1/weather/current")
    suspend fun getCurrentWeather(
        @Query("city") city: String? = null,
        @Query("lat") lat: Double? = null,
        @Query("lon") lon: Double? = null,
        @Query("lang") lang: String = "en"
    ): Response<ApiResponse<CurrentWeather>>

    @GET("api/v1/weather/forecast")
    suspend fun getForecast(
        @Query("city") city: String? = null,
        @Query("lat") lat: Double? = null,
        @Query("lon") lon: Double? = null,
        @Query("days") days: Int = 7,
        @Query("lang") lang: String = "en"
    ): Response<ApiResponse<ForecastResponse>>

    @GET("api/v1/locations/search")
    suspend fun searchLocations(
        @Query("query") query: String,
        @Query("limit") limit: Int = 5
    ): Response<ApiResponse<List<LocationInfo>>>

    @GET("api/v1/alerts")
    suspend fun getAlerts(
        @Query("city") city: String? = null,
        @Query("lat") lat: Double? = null,
        @Query("lon") lon: Double? = null,
        @Query("lang") lang: String = "en"
    ): Response<ApiResponse<AlertsResponse>>

    @POST("api/v1/chat")
    suspend fun sendChatMessage(
        @Body request: ChatRequest
    ): Response<ApiResponse<ChatResponse>>
}
