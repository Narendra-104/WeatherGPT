package com.weathergpt.app.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weathergpt.app.data.model.*
import com.weathergpt.app.data.repository.WeatherRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

sealed interface UiState<out T> {
    object Idle : UiState<Nothing>
    object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String) : UiState<Nothing>
}

data class CompareState(
    val city1: String = "Delhi",
    val city2: String = "Mumbai",
    val weather1: CurrentWeather? = null,
    val weather2: CurrentWeather? = null,
    val isLoading: Boolean = false,
    val errorMessage: String? = null
)

class WeatherViewModel(
    private val repository: WeatherRepository = WeatherRepository()
) : ViewModel() {

    private val _currentCity = MutableStateFlow("Delhi")
    val currentCity: StateFlow<String> = _currentCity.asStateFlow()

    private val _language = MutableStateFlow("en")
    val language: StateFlow<String> = _language.asStateFlow()

    private val _weatherState = MutableStateFlow<UiState<CurrentWeather>>(UiState.Loading)
    val weatherState: StateFlow<UiState<CurrentWeather>> = _weatherState.asStateFlow()

    private val _forecastState = MutableStateFlow<UiState<ForecastResponse>>(UiState.Loading)
    val forecastState: StateFlow<UiState<ForecastResponse>> = _forecastState.asStateFlow()

    private val _alertsState = MutableStateFlow<UiState<List<WeatherAlert>>>(UiState.Idle)
    val alertsState: StateFlow<UiState<List<WeatherAlert>>> = _alertsState.asStateFlow()

    private val _chatMessages = MutableStateFlow<List<ChatMessage>>(
        listOf(
            ChatMessage("assistant", "Hello! I am WeatherGPT. How can I help you with weather updates, farm advice, or travel plans today?")
        )
    )
    val chatMessages: StateFlow<List<ChatMessage>> = _chatMessages.asStateFlow()

    private val _isChatLoading = MutableStateFlow(false)
    val isChatLoading: StateFlow<Boolean> = _isChatLoading.asStateFlow()

    private val _compareState = MutableStateFlow(CompareState())
    val compareState: StateFlow<CompareState> = _compareState.asStateFlow()

    init {
        loadWeatherData()
    }

    fun setLanguage(lang: String) {
        if (_language.value != lang) {
            _language.value = lang
            loadWeatherData()
        }
    }

    fun searchCity(city: String) {
        if (city.isNotBlank()) {
            _currentCity.value = city.trim()
            loadWeatherData()
        }
    }

    fun loadByCoordinates(lat: Double, lon: Double) {
        viewModelScope.launch {
            _weatherState.value = UiState.Loading
            _forecastState.value = UiState.Loading
            _alertsState.value = UiState.Loading

            val lang = _language.value

            val weatherResult = repository.getCurrentWeather(lat = lat, lon = lon, lang = lang)
            weatherResult.fold(
                onSuccess = {
                    _weatherState.value = UiState.Success(it)
                    _currentCity.value = it.location.name
                },
                onFailure = { _weatherState.value = UiState.Error(it.message ?: "Failed to load weather") }
            )

            val forecastResult = repository.getForecast(lat = lat, lon = lon, days = 7, lang = lang)
            forecastResult.fold(
                onSuccess = { _forecastState.value = UiState.Success(it) },
                onFailure = { _forecastState.value = UiState.Error(it.message ?: "Failed to load forecast") }
            )

            val alertResult = repository.getAlerts(lat = lat, lon = lon, lang = lang)
            alertResult.fold(
                onSuccess = { _alertsState.value = UiState.Success(it.alerts) },
                onFailure = { _alertsState.value = UiState.Success(emptyList()) }
            )
        }
    }

    fun loadWeatherData() {
        val city = _currentCity.value
        val lang = _language.value

        viewModelScope.launch {
            _weatherState.value = UiState.Loading
            _forecastState.value = UiState.Loading
            _alertsState.value = UiState.Loading

            val weatherResult = repository.getCurrentWeather(city = city, lang = lang)
            weatherResult.fold(
                onSuccess = { _weatherState.value = UiState.Success(it) },
                onFailure = { _weatherState.value = UiState.Error(it.message ?: "Failed to load current weather") }
            )

            val forecastResult = repository.getForecast(city = city, days = 7, lang = lang)
            forecastResult.fold(
                onSuccess = { _forecastState.value = UiState.Success(it) },
                onFailure = { _forecastState.value = UiState.Error(it.message ?: "Failed to load forecast") }
            )

            val alertsResult = repository.getAlerts(city = city, lang = lang)
            alertsResult.fold(
                onSuccess = { _alertsState.value = UiState.Success(it.alerts) },
                onFailure = { _alertsState.value = UiState.Success(emptyList()) }
            )
        }
    }

    fun sendChatMessage(messageText: String) {
        if (messageText.isBlank() || _isChatLoading.value) return

        val userMsg = ChatMessage("user", messageText.trim())
        val updatedList = _chatMessages.value + userMsg
        _chatMessages.value = updatedList
        _isChatLoading.value = true

        viewModelScope.launch {
            val req = ChatRequest(
                message = userMsg.content,
                location = _currentCity.value,
                language = _language.value,
                conversationHistory = updatedList.takeLast(6)
            )

            val result = repository.sendChatMessage(req)
            _isChatLoading.value = false
            result.fold(
                onSuccess = { resp ->
                    _chatMessages.value = _chatMessages.value + ChatMessage("assistant", resp.reply)
                },
                onFailure = { err ->
                    _chatMessages.value = _chatMessages.value + ChatMessage(
                        "assistant",
                        "Sorry, I encountered an issue retrieving live weather details: ${err.message}"
                    )
                }
            )
        }
    }

    fun compareCities(city1: String, city2: String) {
        _compareState.value = _compareState.value.copy(city1 = city1, city2 = city2, isLoading = true, errorMessage = null)
        viewModelScope.launch {
            val res1 = repository.getCurrentWeather(city = city1, lang = _language.value)
            val res2 = repository.getCurrentWeather(city = city2, lang = _language.value)

            if (res1.isSuccess && res2.isSuccess) {
                _compareState.value = _compareState.value.copy(
                    weather1 = res1.getOrNull(),
                    weather2 = res2.getOrNull(),
                    isLoading = false
                )
            } else {
                _compareState.value = _compareState.value.copy(
                    isLoading = false,
                    errorMessage = "Failed to compare cities. Please ensure both names are valid."
                )
            }
        }
    }
}
