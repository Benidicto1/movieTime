package com.movietime.app.ui.player

import android.view.ViewGroup
import android.widget.FrameLayout
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView
import androidx.media3.common.MediaItem
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView

@Composable
fun VideoPlayerScreen(
    streamUrl: String
) {

    val context =
        androidx.compose.ui.platform
            .LocalContext
            .current

    val exoPlayer =
        remember(streamUrl) {

            ExoPlayer.Builder(
                context
            )
                .build()
                .apply {

                    val mediaItem =
                        MediaItem.fromUri(
                            streamUrl
                        )

                    setMediaItem(
                        mediaItem
                    )

                    prepare()

                    playWhenReady = true
                }
        }

    DisposableEffect(
        exoPlayer
    ) {

        onDispose {

            exoPlayer.release()
        }
    }

    AndroidView(

        modifier = Modifier.fillMaxSize(),

        factory = {

            PlayerView(it).apply {

                player =
                    exoPlayer

                layoutParams =
                    FrameLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.MATCH_PARENT
                    )
            }
        },

        update = { playerView ->

            playerView.player =
                exoPlayer
        }
    )
}