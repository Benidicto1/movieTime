package com.movietime.app.data.model

data class Movie(

    val id: Int,

    val title: String,

    val description: String,

    val posterUrl: String?,

    val releaseDate: String?,

    val rating: Double?

)