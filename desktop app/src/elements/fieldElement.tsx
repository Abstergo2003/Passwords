import "../styles/fieldElement.css"

export function FieldElement(props: {
    name: string,
    value: string
}) {

    const handleOnClick = () => {
        //copy value to clipboard
    }

    return (
        <div className="field">
            <span>{props.name}</span>
            <input value={props.value}/>
            <button onClick={handleOnClick}></button>
        </div>
    )
}