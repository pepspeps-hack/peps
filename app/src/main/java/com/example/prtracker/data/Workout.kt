package com.example.prtracker.data

import java.util.Date

data class Workout(
    val date: Date,
    val exercises: List<Exercise>
)