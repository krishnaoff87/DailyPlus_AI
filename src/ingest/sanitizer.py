"""
Local text sanitizer for masking and unmasking sensitive information.

This module provides the LocalSanitizer class for detecting and replacing
sensitive data (emails, phone numbers) with placeholder tokens, and restoring
the original values when needed.
"""

import re
from typing import Dict


class LocalSanitizer:
    """
    A sanitizer class for masking and unmasking sensitive information in text.

    This class detects sensitive data such as email addresses and phone numbers,
    replaces them with placeholder tokens, and maintains a bidirectional lookup
    table to restore the original values when needed.

    Attributes:
        lookup_table (Dict[str, str]): Bidirectional mapping between placeholders
            and original sensitive values. Contains both forward (placeholder → original)
            and reverse (original → placeholder) mappings.
        _email_counter (int): Counter for generating sequential email placeholders.
        _phone_counter (int): Counter for generating sequential phone placeholders.

    Example:
        >>> sanitizer = LocalSanitizer()
        >>> masked = sanitizer.mask_text("Contact: john@example.com or 555-123-4567")
        >>> print(masked)
        Contact: [REDACTED_EMAIL_0] or [REDACTED_PHONE_0]
        >>> original = sanitizer.unmask_text(masked)
        >>> print(original)
        Contact: john@example.com or 555-123-4567
    """

    # Compile regex patterns at class level for performance
    # RFC 5322 simplified email pattern - matches most common email formats
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

    # Phone patterns:
    # 1. Continuous 10-digit format: 1234567890
    # 2. Hyphenated format: XXX-XXX-XXXX (e.g., 555-123-4567)
    PHONE_PATTERN_CONTINUOUS = re.compile(r"\b\d{10}\b")
    PHONE_PATTERN_HYPHENATED = re.compile(r"\b\d{3}-\d{3}-\d{4}\b")

    def __init__(self) -> None:
        """
        Initialize the LocalSanitizer with an empty lookup table and counters.

        The lookup table will store bidirectional mappings between placeholders
        and original values as sensitive data is detected and masked.
        """
        self.lookup_table: Dict[str, str] = {}
        self._email_counter: int = 0
        self._phone_counter: int = 0

    def mask_text(self, text: str) -> str:
        """
        Mask sensitive information in the provided text.

        Detects email addresses and phone numbers using compiled regex patterns,
        replaces them with sequential placeholder tokens, and stores bidirectional
        mappings in the lookup table for later restoration.

        Args:
            text (str): The input text containing potential sensitive information.

        Returns:
            str: The masked text with sensitive data replaced by placeholders.
                Returns the original text unchanged if an error occurs during processing.

        Raises:
            No exceptions are raised; errors are caught and handled gracefully.

        Example:
            >>> sanitizer = LocalSanitizer()
            >>> masked = sanitizer.mask_text("Email me at alice@example.com")
            >>> print(masked)
            Email me at [REDACTED_EMAIL_0]
        """
        try:
            masked_text = text

            # Process emails first
            email_matches = self.EMAIL_PATTERN.finditer(masked_text)
            for match in email_matches:
                original_email = match.group(0)

                # Check if this email has already been masked
                if original_email not in self.lookup_table:
                    # Generate new placeholder
                    placeholder = f"[REDACTED_EMAIL_{self._email_counter}]"
                    self._email_counter += 1

                    # Store bidirectional mappings
                    self.lookup_table[placeholder] = (
                        original_email  # Forward: placeholder → original
                    )
                    self.lookup_table[original_email] = (
                        placeholder  # Reverse: original → placeholder
                    )
                else:
                    # Use existing placeholder
                    placeholder = self.lookup_table[original_email]

                # Replace the email with placeholder
                masked_text = masked_text.replace(original_email, placeholder)

            # Process hyphenated phone numbers (XXX-XXX-XXXX)
            phone_matches_hyphenated = self.PHONE_PATTERN_HYPHENATED.finditer(
                masked_text
            )
            for match in phone_matches_hyphenated:
                original_phone = match.group(0)

                # Check if this phone number has already been masked
                if original_phone not in self.lookup_table:
                    # Generate new placeholder
                    placeholder = f"[REDACTED_PHONE_{self._phone_counter}]"
                    self._phone_counter += 1

                    # Store bidirectional mappings
                    self.lookup_table[placeholder] = (
                        original_phone  # Forward: placeholder → original
                    )
                    self.lookup_table[original_phone] = (
                        placeholder  # Reverse: original → placeholder
                    )
                else:
                    # Use existing placeholder
                    placeholder = self.lookup_table[original_phone]

                # Replace the phone number with placeholder
                masked_text = masked_text.replace(original_phone, placeholder)

            # Process continuous 10-digit phone numbers (1234567890)
            phone_matches_continuous = self.PHONE_PATTERN_CONTINUOUS.finditer(
                masked_text
            )
            for match in phone_matches_continuous:
                original_phone = match.group(0)

                # Check if this phone number has already been masked
                if original_phone not in self.lookup_table:
                    # Generate new placeholder
                    placeholder = f"[REDACTED_PHONE_{self._phone_counter}]"
                    self._phone_counter += 1

                    # Store bidirectional mappings
                    self.lookup_table[placeholder] = (
                        original_phone  # Forward: placeholder → original
                    )
                    self.lookup_table[original_phone] = (
                        placeholder  # Reverse: original → placeholder
                    )
                else:
                    # Use existing placeholder
                    placeholder = self.lookup_table[original_phone]

                # Replace the phone number with placeholder
                masked_text = masked_text.replace(original_phone, placeholder)

            return masked_text

        except Exception:
            # Graceful degradation: return original text if any error occurs
            # In production, you might want to log this error
            return text

    def unmask_text(self, text: str) -> str:
        """
        Restore original sensitive information from masked text.

        Iterates through the lookup table and replaces all placeholder tokens
        with their corresponding original values.

        Args:
            text (str): The masked text containing placeholder tokens.

        Returns:
            str: The unmasked text with placeholders restored to original values.
                Returns the original text unchanged if an error occurs during processing.

        Raises:
            No exceptions are raised; errors are caught and handled gracefully.

        Example:
            >>> sanitizer = LocalSanitizer()
            >>> masked = sanitizer.mask_text("Call 555-123-4567")
            >>> unmasked = sanitizer.unmask_text(masked)
            >>> print(unmasked)
            Call 555-123-4567
        """
        try:
            unmasked_text = text

            # Iterate through lookup table and restore placeholders
            # We only need to process placeholder → original mappings
            for key, value in self.lookup_table.items():
                # Check if key is a placeholder (starts with [REDACTED_)
                if key.startswith("[REDACTED_"):
                    # Replace placeholder with original value
                    unmasked_text = unmasked_text.replace(key, value)

            return unmasked_text

        except Exception:
            # Graceful degradation: return original text if any error occurs
            # In production, you might want to log this error
            return text


# Made with Bob
