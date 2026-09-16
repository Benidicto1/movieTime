package com.movietime.app.ui.categories

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun CategoriesScreen(
    onCategoryClick: (Category) -> Unit
) {

    val categories = remember {
        listOf(
            Category(1, "Action"),
            Category(2, "Comedy"),
            Category(3, "Drama"),
            Category(4, "Horror"),
            Category(5, "Romance"),
            Category(6, "Thriller"),
            Category(7, "Science Fiction"),
            Category(8, "Animation")
        )
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {

        Text(
            text = "Categories",
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(bottom = 16.dp)
        )

        LazyVerticalGrid(
            columns = GridCells.Fixed(2),
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(
                bottom = 16.dp
            ),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {

            items(categories) { category ->

                CategoryCard(
                    category = category,
                    onClick = {
                        onCategoryClick(category)
                    }
                )
            }
        }
    }
}

@Composable
private fun CategoryCard(
    category: Category,
    onClick: () -> Unit
) {

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable {
                onClick()
            }
    ) {

        Text(
            text = category.name,
            style = MaterialTheme.typography.titleMedium,
            modifier = Modifier.padding(24.dp)
        )
    }
}