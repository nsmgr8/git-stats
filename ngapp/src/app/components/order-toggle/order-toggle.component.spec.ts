import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { OrderToggleComponent } from './order-toggle.component';

describe('OrderToggleComponent', () => {
  let component: OrderToggleComponent;
  let fixture: ComponentFixture<OrderToggleComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ OrderToggleComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(OrderToggleComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
