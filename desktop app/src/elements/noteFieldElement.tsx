export function NoteField(props: {
    value: string
}) {

    const handleOnClick = () => {
        //copy value to clipboard
    }

    return (
        <div className="field">
            <div contentEditable="true">{props.value}</div>
            <button onClick={handleOnClick}></button>
        </div>
    )
}