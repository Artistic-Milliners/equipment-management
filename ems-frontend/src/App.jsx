import "./App.css";
import rippedCircle from './assets/logo1.svg';

function App() {
  return (
    <>
      <div className="container">
        <img className="top-circle-img" src={rippedCircle} alt="" />
        <div className="top-circle-left"></div>
        <div className="left-circle"></div>
        <div className="top-circle-right"></div>
        <div className="right-circle"></div>
        <div className="bottom-circle"></div>
        <img className="logo-img" src={rippedCircle} alt="" />
        <div className="inner-container">
          <div className="top-bar">
            <img src="" alt="" />
          </div>
          <p className="main-heading">WELCOME to your Maintenance 911</p>

          <form action="" method="post">
            <div className="">
              <input type="text" name="username" id="username" placeholder="User Name"/>
              <i className="material-symbols-rounded">person</i>
            </div>
            <div className="">
              <input type="password" name="password" id="password" placeholder="Password"/>
              <i className="material-symbols-rounded">lock</i>
            </div>

            <button>Log In</button>
          </form>
        </div>
      </div>
    </>
  );
}

export default App;
