from indic_transliteration import sanscript


def transliterate_to_roman(text: str) -> str:
    # text = text.lower()
    raw = sanscript.transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
    return raw.lower()


if __name__ == "__main__":
    sample = "तो यार आज के दिन भी coding continue"
    result = transliterate_to_roman(sample)

    print(f"Original:      {sample}")
    print(f"Transliterated: {result}")