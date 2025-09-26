package com.example.prtracker

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.prtracker.data.Exercise
import com.example.prtracker.data.PerformanceSet
import java.util.Date

class MainActivity : AppCompatActivity() {

    private lateinit var exerciseNameInput: EditText
    private lateinit var weightInput: EditText
    private lateinit var repsInput: EditText
    private lateinit var addSetButton: Button
    private lateinit var loggedSetsText: TextView

    private val currentExercises = mutableListOf<Exercise>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        exerciseNameInput = findViewById(R.id.exercise_name_input)
        weightInput = findViewById(R.id.weight_input)
        repsInput = findViewById(R.id.reps_input)
        addSetButton = findViewById(R.id.add_set_button)
        loggedSetsText = findViewById(R.id.logged_sets_text)

        addSetButton.setOnClickListener {
            addSet()
        }
    }

    private fun addSet() {
        val exerciseName = exerciseNameInput.text.toString()
        val weightStr = weightInput.text.toString()
        val repsStr = repsInput.text.toString()

        if (exerciseName.isBlank() || weightStr.isBlank() || repsStr.isBlank()) {
            Toast.makeText(this, "Please fill all fields", Toast.LENGTH_SHORT).show()
            return
        }

        val weight = weightStr.toDoubleOrNull()
        val reps = repsStr.toIntOrNull()

        if (weight == null || reps == null) {
            Toast.makeText(this, "Invalid weight or reps", Toast.LENGTH_SHORT).show()
            return
        }

        val newSet = PerformanceSet(reps, weight)

        val existingExercise = currentExercises.find { it.name.equals(exerciseName, ignoreCase = true) }

        if (existingExercise != null) {
            (existingExercise.sets as MutableList).add(newSet)
        } else {
            val newExercise = Exercise(exerciseName, mutableListOf(newSet))
            currentExercises.add(newExercise)
        }

        updateLoggedSetsText()
        clearInputs()
    }

    private fun updateLoggedSetsText() {
        val stringBuilder = StringBuilder()
        stringBuilder.append("Logged Sets:\n")
        currentExercises.forEach { exercise ->
            stringBuilder.append("\n${exercise.name}:\n")
            exercise.sets.forEachIndexed { index, set ->
                stringBuilder.append("  Set ${index + 1}: ${set.reps} reps at ${set.weight} kg\n")
            }
        }
        loggedSetsText.text = stringBuilder.toString()
    }

    private fun clearInputs() {
        // Keep exercise name for convenience
        weightInput.text.clear()
        repsInput.text.clear()
        weightInput.requestFocus()
    }
}