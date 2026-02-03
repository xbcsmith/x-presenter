def remove_unused_placeholders(slide, has_title: bool, has_body_content: bool) -> None:
    """Remove unused placeholder shapes from slide.

    PowerPoint layouts include placeholder shapes (title, body) that should
    be removed if not used. This prevents empty placeholders from appearing
    in the presentation.

    Args:
        slide: PowerPoint slide object
        has_title: Whether slide has title content
        has_body_content: Whether slide has body content (lists, paragraphs, images)

    Returns:
        None

    Side Effects:
        Removes unused placeholder shapes from the slide
    """
    shapes_to_delete = []

    for shape in slide.shapes:
        # Check if it's a placeholder
        if shape.is_placeholder:
            placeholder = shape.placeholder_format
            # Type 1 is title placeholder
            # Type 2 is body/content placeholder
            if placeholder.type == 1 and not has_title:  # Title placeholder unused
                shapes_to_delete.append(shape)
            elif (
                placeholder.type == 2 and has_body_content
            ):  # Body placeholder unused (we create our own)
                shapes_to_delete.append(shape)

    # Remove the shapes (must be done after iteration)
    for shape in shapes_to_delete:
        sp = shape.element
        sp.getparent().remove(sp)
