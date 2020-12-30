export default function Errors(props) {
  if (props.errors.length < 1) {
    return null;
  }

  return (
    <div className="alert alert-danger">
      <ul className="mb-0">
        {
          props.errors.map((error, i) => <li key={i}>{error}</li>)
        }
      </ul>
    </div>
  );
}
