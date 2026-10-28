package com.weathergpt.app

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.speech.RecognizerIntent
import android.speech.tts.TextToSpeech
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CompareArrows
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Psychology
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.weathergpt.app.ui.screens.ChatScreen
import com.weathergpt.app.ui.screens.CompareScreen
import com.weathergpt.app.ui.screens.HomeScreen
import com.weathergpt.app.ui.theme.DarkBackground
import com.weathergpt.app.ui.theme.DarkSurface
import com.weathergpt.app.ui.theme.WeatherGPTTheme
import com.weathergpt.app.ui.viewmodel.WeatherViewModel
import java.util.*

class MainActivity : ComponentActivity(), TextToSpeech.OnInitListener {

    private val viewModel: WeatherViewModel by viewModels()
    private var textToSpeech: TextToSpeech? = null

    private val voiceInputLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK && result.data != null) {
            val spokenText = result.data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)?.firstOrNull()
            if (!spokenText.isNullOrBlank()) {
                viewModel.sendChatMessage(spokenText)
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        textToSpeech = TextToSpeech(this, this)

        setContent {
            WeatherGPTTheme {
                MainAppScaffold(
                    viewModel = viewModel,
                    onSpeak = { text -> speakText(text) },
                    onStartVoice = { launchVoiceRecognizer() }
                )
            }
        }
    }

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            textToSpeech?.language = Locale.ENGLISH
        }
    }

    private fun speakText(text: String) {
        textToSpeech?.let { tts ->
            tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "WeatherGPT_TTS")
        } ?: Toast.makeText(this, "Text-to-speech not ready", Toast.LENGTH_SHORT).show()
    }

    private fun launchVoiceRecognizer() {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_PROMPT, "Ask WeatherGPT...")
        }
        try {
            voiceInputLauncher.launch(intent)
        } catch (e: Exception) {
            Toast.makeText(this, "Voice recognition not available on this device", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onDestroy() {
        textToSpeech?.stop()
        textToSpeech?.shutdown()
        super.onDestroy()
    }
}

sealed class Screen(val route: String, val titleRes: Int, val icon: androidx.compose.ui.graphics.vector.ImageVector) {
    object Home : Screen("home", R.string.nav_home, Icons.Default.Home)
    object Chat : Screen("chat", R.string.nav_chat, Icons.Default.Psychology)
    object Compare : Screen("compare", R.string.nav_compare, Icons.Default.CompareArrows)
}

@Composable
fun MainAppScaffold(
    viewModel: WeatherViewModel,
    onSpeak: (String) -> Unit,
    onStartVoice: () -> Unit
) {
    val navController = rememberNavController()
    val screens = listOf(Screen.Home, Screen.Chat, Screen.Compare)
    var selectedRoute by remember { mutableStateOf(Screen.Home.route) }

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        containerColor = DarkBackground,
        bottomBar = {
            NavigationBar(
                containerColor = DarkSurface
            ) {
                screens.forEach { screen ->
                    val isSelected = selectedRoute == screen.route
                    NavigationBarItem(
                        icon = { Icon(screen.icon, contentDescription = stringResource(screen.titleRes)) },
                        label = { Text(stringResource(screen.titleRes)) },
                        selected = isSelected,
                        onClick = {
                            selectedRoute = screen.route
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.startDestinationId) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        }
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Home.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.Home.route) {
                HomeScreen(
                    viewModel = viewModel,
                    onNavigateToChat = {
                        selectedRoute = Screen.Chat.route
                        navController.navigate(Screen.Chat.route)
                    }
                )
            }
            composable(Screen.Chat.route) {
                ChatScreen(
                    viewModel = viewModel,
                    onSpeak = onSpeak,
                    onStartVoiceRecognition = onStartVoice
                )
            }
            composable(Screen.Compare.route) {
                CompareScreen(viewModel = viewModel)
            }
        }
    }
}
