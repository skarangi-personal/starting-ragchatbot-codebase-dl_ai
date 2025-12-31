"""Tests for Pydantic models used in the application."""

import pytest
from models import Course, Lesson, CourseChunk


class TestLesson:
    """Test suite for the Lesson model."""

    def test_lesson_creation_with_all_fields(self):
        """Test creating a lesson with all fields."""
        lesson = Lesson(
            lesson_number=1,
            title="Getting Started",
            lesson_link="https://example.com/lesson1"
        )

        assert lesson.lesson_number == 1
        assert lesson.title == "Getting Started"
        assert lesson.lesson_link == "https://example.com/lesson1"

    def test_lesson_creation_without_link(self):
        """Test creating a lesson without lesson link."""
        lesson = Lesson(
            lesson_number=2,
            title="Advanced Topics"
        )

        assert lesson.lesson_number == 2
        assert lesson.title == "Advanced Topics"
        assert lesson.lesson_link is None

    def test_lesson_model_validation(self):
        """Test that Lesson model validates required fields."""
        # Missing required 'lesson_number'
        with pytest.raises(ValueError):
            Lesson(title="Test")


class TestCourse:
    """Test suite for the Course model."""

    def test_course_creation_with_all_fields(self):
        """Test creating a course with all fields."""
        lessons = [
            Lesson(lesson_number=1, title="Intro"),
            Lesson(lesson_number=2, title="Advanced")
        ]

        course = Course(
            title="Python Basics",
            course_link="https://example.com/python",
            instructor="John Doe",
            lessons=lessons
        )

        assert course.title == "Python Basics"
        assert course.course_link == "https://example.com/python"
        assert course.instructor == "John Doe"
        assert len(course.lessons) == 2

    def test_course_creation_with_minimal_fields(self):
        """Test creating a course with only required fields."""
        course = Course(title="Python Basics")

        assert course.title == "Python Basics"
        assert course.course_link is None
        assert course.instructor is None
        assert course.lessons == []

    def test_course_with_empty_lessons_list(self):
        """Test course with explicitly empty lessons list."""
        course = Course(
            title="Test Course",
            lessons=[]
        )

        assert course.lessons == []

    def test_course_model_validation(self):
        """Test that Course model validates required fields."""
        with pytest.raises(ValueError):
            # Missing required 'title'
            Course(course_link="https://example.com")


class TestCourseChunk:
    """Test suite for the CourseChunk model."""

    def test_chunk_creation_with_all_fields(self):
        """Test creating a chunk with all fields."""
        chunk = CourseChunk(
            content="Python is a programming language.",
            course_title="Python Basics",
            lesson_number=1,
            chunk_index=0
        )

        assert chunk.content == "Python is a programming language."
        assert chunk.course_title == "Python Basics"
        assert chunk.lesson_number == 1
        assert chunk.chunk_index == 0

    def test_chunk_creation_without_lesson_number(self):
        """Test creating a chunk without lesson number."""
        chunk = CourseChunk(
            content="Metadata about the course.",
            course_title="Python Basics",
            chunk_index=0
        )

        assert chunk.content == "Metadata about the course."
        assert chunk.course_title == "Python Basics"
        assert chunk.lesson_number is None
        assert chunk.chunk_index == 0

    def test_chunk_with_long_content(self):
        """Test chunk with very long content."""
        long_content = "Test content. " * 1000
        chunk = CourseChunk(
            content=long_content,
            course_title="Test Course",
            chunk_index=0
        )

        assert chunk.content == long_content
        assert len(chunk.content) > 10000

    def test_chunk_model_validation(self):
        """Test that CourseChunk model validates required fields."""
        # Missing required 'content'
        with pytest.raises(ValueError):
            CourseChunk(
                course_title="Test",
                chunk_index=0
            )

        # Missing required 'course_title'
        with pytest.raises(ValueError):
            CourseChunk(
                content="Test",
                chunk_index=0
            )

        # Missing required 'chunk_index'
        with pytest.raises(ValueError):
            CourseChunk(
                content="Test",
                course_title="Course"
            )


class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_lesson_to_dict(self):
        """Test converting Lesson to dictionary."""
        lesson = Lesson(
            lesson_number=1,
            title="Test",
            lesson_link="https://example.com"
        )

        lesson_dict = lesson.model_dump()
        assert lesson_dict["lesson_number"] == 1
        assert lesson_dict["title"] == "Test"
        assert lesson_dict["lesson_link"] == "https://example.com"

    def test_course_to_json(self):
        """Test converting Course to JSON string."""
        course = Course(title="Test Course")

        course_json = course.model_dump_json()
        assert "Test Course" in course_json
        assert isinstance(course_json, str)

    def test_chunk_from_dict(self):
        """Test creating CourseChunk from dictionary."""
        chunk_data = {
            "content": "Test content",
            "course_title": "Test Course",
            "lesson_number": 1,
            "chunk_index": 0
        }

        chunk = CourseChunk(**chunk_data)
        assert chunk.content == "Test content"
        assert chunk.course_title == "Test Course"

    def test_course_with_nested_lessons(self):
        """Test course with nested lesson objects."""
        course_data = {
            "title": "Test Course",
            "lessons": [
                {"lesson_number": 1, "title": "Lesson 1"},
                {"lesson_number": 2, "title": "Lesson 2"}
            ]
        }

        course = Course(**course_data)
        assert len(course.lessons) == 2
        assert course.lessons[0].lesson_number == 1
        assert isinstance(course.lessons[0], Lesson)
