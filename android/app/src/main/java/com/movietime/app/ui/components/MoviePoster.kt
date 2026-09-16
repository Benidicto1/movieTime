package com.movietime.app.ui.components

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import coil3.compose.SubcomposeAsyncImage

@Composable
fun MoviePoster(
    posterUrl: String?,
    modifier: Modifier = Modifier
) {

    if (posterUrl.isNullOrBlank()) {

        Box(
            modifier = modifier
                .fillMaxWidth()
                .height(220.dp)
                .clip(
                    RoundedCornerShape(12.dp)
                ),
            contentAlignment = Alignment.Center
        ) {

            Text(
                text = "No poster available",
                color = MaterialTheme
                    .colorScheme
                    .onSurfaceVariant
            )
        }

        return
    }

    SubcomposeAsyncImage(
        model = posterUrl,
        contentDescription = "Movie poster",
        modifier = modifier
            .fillMaxWidth()
            .height(220.dp)
            .clip(
                RoundedCornerShape(12.dp)
            ),
        contentScale = ContentScale.Crop,

        loading = {

            Box(
                modifier = Modifier.fillMaxWidth(),
                contentAlignment = Alignment.Center
            ) {

                CircularProgressIndicator()
            }
        },

        error = {

            Box(
                modifier = Modifier.fillMaxWidth(),
                contentAlignment = Alignment.Center
            ) {

                Text(
                    text = "Unable to load poster",
                    color = MaterialTheme
                        .colorScheme
                        .error
                )
            }
        }
    )
}